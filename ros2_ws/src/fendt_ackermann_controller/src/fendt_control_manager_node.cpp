#include <algorithm>
#include <cmath>
#include <memory>

#include "geometry_msgs/msg/twist.hpp"
#include "lifecycle_msgs/msg/state.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/lifecycle_node.hpp"
#include "std_msgs/msg/bool.hpp"

namespace fendt_ackermann_controller
{

class FendtControlManager : public rclcpp_lifecycle::LifecycleNode
{
public:
  FendtControlManager()
  : rclcpp_lifecycle::LifecycleNode("fendt_control_manager")
  {
    declare_parameter<std::string>("input_cmd_vel_topic", "/cmd_vel");
    declare_parameter<std::string>("output_cmd_vel_topic", "/cmd_vel_safe");
    declare_parameter<std::string>("brake_active_topic", "/fendt/brake_active");
    declare_parameter<double>("cmd_vel_timeout", 0.5);
    declare_parameter<double>("max_steering_angle", 0.7853981634);
    declare_parameter<double>("wheelbase", 2.37);
  }

private:
  using CallbackReturn = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

  CallbackReturn on_configure(const rclcpp_lifecycle::State &) override
  {
    input_cmd_vel_topic_ = get_parameter("input_cmd_vel_topic").as_string();
    output_cmd_vel_topic_ = get_parameter("output_cmd_vel_topic").as_string();
    brake_active_topic_ = get_parameter("brake_active_topic").as_string();
    cmd_vel_timeout_ = std::max(0.0, get_parameter("cmd_vel_timeout").as_double());
    max_steering_angle_ = std::abs(get_parameter("max_steering_angle").as_double());
    wheelbase_ = get_parameter("wheelbase").as_double();

    if (wheelbase_ <= 0.0) {
      RCLCPP_ERROR(get_logger(), "wheelbase must be > 0.0");
      return CallbackReturn::ERROR;
    }

    safe_cmd_pub_ = create_publisher<geometry_msgs::msg::Twist>(output_cmd_vel_topic_, 10);
    brake_pub_ = create_publisher<std_msgs::msg::Bool>(brake_active_topic_, 10);

    cmd_sub_ = create_subscription<geometry_msgs::msg::Twist>(
      input_cmd_vel_topic_,
      rclcpp::SystemDefaultsQoS(),
      std::bind(&FendtControlManager::onCmdVel, this, std::placeholders::_1));

    timer_ = create_wall_timer(
      std::chrono::milliseconds(20),
      std::bind(&FendtControlManager::publishSafeCommand, this));

    last_cmd_time_ = now();
    latest_cmd_ = geometry_msgs::msg::Twist();
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_activate(const rclcpp_lifecycle::State &) override
  {
    safe_cmd_pub_->on_activate();
    brake_pub_->on_activate();
    publishStopped(true);
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_deactivate(const rclcpp_lifecycle::State &) override
  {
    publishStopped(true);
    safe_cmd_pub_->on_deactivate();
    brake_pub_->on_deactivate();
    return CallbackReturn::SUCCESS;
  }

  CallbackReturn on_cleanup(const rclcpp_lifecycle::State &) override
  {
    timer_.reset();
    cmd_sub_.reset();
    safe_cmd_pub_.reset();
    brake_pub_.reset();
    return CallbackReturn::SUCCESS;
  }

  void onCmdVel(const geometry_msgs::msg::Twist::SharedPtr msg)
  {
    latest_cmd_ = *msg;
    last_cmd_time_ = now();
  }

  static double clamp(double value, double low, double high)
  {
    return std::min(std::max(value, low), high);
  }

  void publishStopped(bool brake_active)
  {
    if (
      get_current_state().id() != lifecycle_msgs::msg::State::PRIMARY_STATE_ACTIVE ||
      !safe_cmd_pub_ || !brake_pub_)
    {
      return;
    }

    geometry_msgs::msg::Twist stopped_cmd;
    safe_cmd_pub_->publish(stopped_cmd);

    std_msgs::msg::Bool brake_msg;
    brake_msg.data = brake_active;
    brake_pub_->publish(brake_msg);
  }

  void publishSafeCommand()
  {
    if (get_current_state().id() != lifecycle_msgs::msg::State::PRIMARY_STATE_ACTIVE) {
      return;
    }

    const double age = (now() - last_cmd_time_).seconds();
    if (age > cmd_vel_timeout_) {
      publishStopped(true);
      return;
    }

    geometry_msgs::msg::Twist safe_cmd = latest_cmd_;
    bool brake_active = false;

    if (!std::isfinite(safe_cmd.linear.x) || !std::isfinite(safe_cmd.angular.z)) {
      publishStopped(true);
      return;
    }

    if (std::abs(safe_cmd.linear.x) < 1e-6) {
      safe_cmd.angular.z = 0.0;
      brake_active = true;
    } else {
      const double steering_angle = std::atan2(wheelbase_ * safe_cmd.angular.z, safe_cmd.linear.x);
      const double clamped = clamp(steering_angle, -max_steering_angle_, max_steering_angle_);
      safe_cmd.angular.z = std::tan(clamped) * safe_cmd.linear.x / wheelbase_;
    }

    safe_cmd_pub_->publish(safe_cmd);
    std_msgs::msg::Bool brake_msg;
    brake_msg.data = brake_active;
    brake_pub_->publish(brake_msg);
  }

  std::string input_cmd_vel_topic_;
  std::string output_cmd_vel_topic_;
  std::string brake_active_topic_;

  double cmd_vel_timeout_{0.5};
  double max_steering_angle_{0.7853981634};
  double wheelbase_{2.37};

  geometry_msgs::msg::Twist latest_cmd_;
  rclcpp::Time last_cmd_time_{0, 0, RCL_ROS_TIME};

  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_sub_;
  rclcpp_lifecycle::LifecyclePublisher<geometry_msgs::msg::Twist>::SharedPtr safe_cmd_pub_;
  rclcpp_lifecycle::LifecyclePublisher<std_msgs::msg::Bool>::SharedPtr brake_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

}  // namespace fendt_ackermann_controller

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<fendt_ackermann_controller::FendtControlManager>();
  rclcpp::spin(node->get_node_base_interface());
  rclcpp::shutdown();
  return 0;
}

