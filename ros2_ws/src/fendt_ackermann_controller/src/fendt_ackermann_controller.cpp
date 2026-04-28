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
  auto_declare<double>("rear_wheel_radius", 0.78);
  auto_declare<double>("max_steering_angle", 0.7853981634);
  auto_declare<double>("cmd_vel_timeout", 0.5);
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
  rear_wheel_radius_ = get_node()->get_parameter("rear_wheel_radius").as_double();
  max_steering_angle_ = std::abs(get_node()->get_parameter("max_steering_angle").as_double());
  cmd_vel_timeout_ = std::max(0.0, get_node()->get_parameter("cmd_vel_timeout").as_double());

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
  return controller_interface::CallbackReturn::SUCCESS;
}

controller_interface::CallbackReturn FendtAckermannController::on_deactivate(
  const rclcpp_lifecycle::State &)
{
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
  const rclcpp::Duration &)
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

  double steering_angle = 0.0;
  if (std::abs(linear_x) > 1e-6 && std::abs(angular_z) > 1e-6) {
    steering_angle = std::atan(wheelbase_ * angular_z / linear_x);
  }
  steering_angle = clamp(steering_angle, -max_steering_angle_, max_steering_angle_);

  const double rear_wheel_velocity = linear_x / rear_wheel_radius_;

  command_interfaces_[0].set_value(steering_angle);
  command_interfaces_[1].set_value(steering_angle);
  command_interfaces_[2].set_value(rear_wheel_velocity);
  command_interfaces_[3].set_value(rear_wheel_velocity);

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

}  // namespace fendt_ackermann_controller

PLUGINLIB_EXPORT_CLASS(
  fendt_ackermann_controller::FendtAckermannController,
  controller_interface::ControllerInterface)

