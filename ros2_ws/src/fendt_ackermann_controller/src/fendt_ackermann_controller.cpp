#include "fendt_ackermann_controller/fendt_ackermann_controller.hpp"

#include <algorithm>
#include <cmath>
#include <vector>

#include "pluginlib/class_list_macros.hpp"
#include "rclcpp/rclcpp.hpp"

namespace fendt_ackermann_controller
{

controller_interface::CallbackReturn FendtAckermannController::on_init()
{
  auto_declare<std::string>("cmd_vel_topic", "/cmd_vel");
  auto_declare<std::string>("front_left_steer_joint", "front_left_wheel_steer_joint");
  auto_declare<std::string>("front_right_steer_joint", "front_right_wheel_steer_joint");
  auto_declare<std::string>("rear_left_wheel_joint", "rear_left_wheel_joint");
  auto_declare<std::string>("rear_right_wheel_joint", "rear_right_wheel_joint");
  auto_declare<double>("wheelbase", 2.37);
  auto_declare<double>("traction_track_width", 1.66);
  auto_declare<double>("steering_track_width", 0.0);
  auto_declare<double>("rear_wheel_radius", 0.78);
  auto_declare<double>("max_steering_angle", 0.7853981634);
  auto_declare<double>("cmd_vel_timeout", 0.5);
  auto_declare<double>("steering_rate_limit", 0.2617993878);
  auto_declare<double>("linear_deadband", 0.02);
  auto_declare<double>("angular_deadband", 0.02);
  return controller_interface::CallbackReturn::SUCCESS;
}

controller_interface::CallbackReturn FendtAckermannController::on_configure(
  const rclcpp_lifecycle::State &)
{
  cmd_vel_topic_ = get_node()->get_parameter("cmd_vel_topic").as_string();
  front_left_steer_joint_ = get_node()->get_parameter("front_left_steer_joint").as_string();
  front_right_steer_joint_ = get_node()->get_parameter("front_right_steer_joint").as_string();
  rear_left_wheel_joint_ = get_node()->get_parameter("rear_left_wheel_joint").as_string();
  rear_right_wheel_joint_ = get_node()->get_parameter("rear_right_wheel_joint").as_string();
  wheelbase_ = get_node()->get_parameter("wheelbase").as_double();
  traction_track_width_ = get_node()->get_parameter("traction_track_width").as_double();
  steering_track_width_ = get_node()->get_parameter("steering_track_width").as_double();
  rear_wheel_radius_ = get_node()->get_parameter("rear_wheel_radius").as_double();
  max_steering_angle_ = std::abs(get_node()->get_parameter("max_steering_angle").as_double());
  cmd_vel_timeout_ = std::max(0.0, get_node()->get_parameter("cmd_vel_timeout").as_double());
  steering_rate_limit_ = std::max(0.0, get_node()->get_parameter("steering_rate_limit").as_double());
  linear_deadband_ = std::max(0.0, get_node()->get_parameter("linear_deadband").as_double());
  angular_deadband_ = std::max(0.0, get_node()->get_parameter("angular_deadband").as_double());

  if (wheelbase_ <= 0.0) {
    RCLCPP_ERROR(get_node()->get_logger(), "wheelbase must be > 0.0");
    return controller_interface::CallbackReturn::ERROR;
  }
  if (traction_track_width_ <= 0.0) {
    RCLCPP_ERROR(get_node()->get_logger(), "traction_track_width must be > 0.0");
    return controller_interface::CallbackReturn::ERROR;
  }
  if (steering_track_width_ <= 0.0) {
    steering_track_width_ = traction_track_width_;
  }
  if (rear_wheel_radius_ <= 0.0) {
    RCLCPP_ERROR(get_node()->get_logger(), "rear_wheel_radius must be > 0.0");
    return controller_interface::CallbackReturn::ERROR;
  }

  cmd_sub_ = get_node()->create_subscription<geometry_msgs::msg::Twist>(
    cmd_vel_topic_,
    rclcpp::SystemDefaultsQoS(),
    std::bind(&FendtAckermannController::cmdVelCallback, this, std::placeholders::_1));

  {
    std::lock_guard<std::mutex> lock(cmd_mutex_);
    latest_cmd_ = Cmd{};
    latest_cmd_.stamp = get_node()->now();
  }

  return controller_interface::CallbackReturn::SUCCESS;
}

controller_interface::CallbackReturn FendtAckermannController::on_activate(
  const rclcpp_lifecycle::State &)
{
  last_left_steer_cmd_ = 0.0;
  last_right_steer_cmd_ = 0.0;
  writeZeroCommands();
  return controller_interface::CallbackReturn::SUCCESS;
}

controller_interface::CallbackReturn FendtAckermannController::on_deactivate(
  const rclcpp_lifecycle::State &)
{
  writeZeroCommands();
  return controller_interface::CallbackReturn::SUCCESS;
}

controller_interface::InterfaceConfiguration
FendtAckermannController::command_interface_configuration() const
{
  controller_interface::InterfaceConfiguration config;
  config.type = controller_interface::interface_configuration_type::INDIVIDUAL;
  config.names = {
    front_left_steer_joint_ + "/position",
    front_right_steer_joint_ + "/position",
    rear_left_wheel_joint_ + "/velocity",
    rear_right_wheel_joint_ + "/velocity",
  };
  return config;
}

controller_interface::InterfaceConfiguration
FendtAckermannController::state_interface_configuration() const
{
  return {controller_interface::interface_configuration_type::NONE, {}};
}

controller_interface::return_type FendtAckermannController::update(
  const rclcpp::Time & time,
  const rclcpp::Duration & period)
{
  Cmd cmd;
  {
    std::lock_guard<std::mutex> lock(cmd_mutex_);
    cmd = latest_cmd_;
  }

  const auto age = (time - cmd.stamp).seconds();
  double linear_x = cmd.linear_x;
  double angular_z = cmd.angular_z;

  if (age > cmd_vel_timeout_) {
    linear_x = 0.0;
    angular_z = 0.0;
  }

  if (std::abs(linear_x) < linear_deadband_) {
    linear_x = 0.0;
  }
  if (std::abs(angular_z) < angular_deadband_) {
    angular_z = 0.0;
  }

  const double eps = 1e-6;
  double left_steer = 0.0;
  double right_steer = 0.0;
  double left_rear_velocity = linear_x / rear_wheel_radius_;
  double right_rear_velocity = linear_x / rear_wheel_radius_;

  if (std::abs(linear_x) > eps && std::abs(angular_z) > eps) {
    const double turn_radius = linear_x / angular_z;
    const double left_rear_path_radius = turn_radius - (traction_track_width_ * 0.5);
    const double right_rear_path_radius = turn_radius + (traction_track_width_ * 0.5);
    const double left_steer_radius = turn_radius - (steering_track_width_ * 0.5);
    const double right_steer_radius = turn_radius + (steering_track_width_ * 0.5);

    left_steer = std::atan(wheelbase_ / left_steer_radius);
    right_steer = std::atan(wheelbase_ / right_steer_radius);
    left_rear_velocity = (angular_z * left_rear_path_radius) / rear_wheel_radius_;
    right_rear_velocity = (angular_z * right_rear_path_radius) / rear_wheel_radius_;
  }

  left_steer = clamp(left_steer, -max_steering_angle_, max_steering_angle_);
  right_steer = clamp(right_steer, -max_steering_angle_, max_steering_angle_);

  // Rate-limit steering so full-lock transition is gradual and realistic.
  if (steering_rate_limit_ > 0.0) {
    const double dt = std::max(0.0, std::min(0.1, period.seconds()));
    const double max_step = steering_rate_limit_ * dt;
    left_steer = clamp(left_steer, last_left_steer_cmd_ - max_step, last_left_steer_cmd_ + max_step);
    right_steer = clamp(right_steer, last_right_steer_cmd_ - max_step, last_right_steer_cmd_ + max_step);
  }

  last_left_steer_cmd_ = left_steer;
  last_right_steer_cmd_ = right_steer;

  command_interfaces_[0].set_value(left_steer);
  command_interfaces_[1].set_value(right_steer);
  command_interfaces_[2].set_value(left_rear_velocity);
  command_interfaces_[3].set_value(right_rear_velocity);

  return controller_interface::return_type::OK;
}

void FendtAckermannController::cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg)
{
  std::lock_guard<std::mutex> lock(cmd_mutex_);
  latest_cmd_.linear_x = msg->linear.x;
  latest_cmd_.angular_z = msg->angular.z;
  latest_cmd_.stamp = get_node()->now();
}

double FendtAckermannController::clamp(double value, double low, double high)
{
  return std::min(std::max(value, low), high);
}

void FendtAckermannController::writeZeroCommands()
{
  if (command_interfaces_.size() != 4U) {
    return;
  }

  last_left_steer_cmd_ = 0.0;
  last_right_steer_cmd_ = 0.0;

  for (auto & command_interface : command_interfaces_) {
    command_interface.set_value(0.0);
  }
}

}  // namespace fendt_ackermann_controller

PLUGINLIB_EXPORT_CLASS(
  fendt_ackermann_controller::FendtAckermannController,
  controller_interface::ControllerInterface)

