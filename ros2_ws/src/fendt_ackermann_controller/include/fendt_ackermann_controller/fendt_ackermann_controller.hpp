#ifndef FENDT_ACKERMANN_CONTROLLER__FENDT_ACKERMANN_CONTROLLER_HPP_
#define FENDT_ACKERMANN_CONTROLLER__FENDT_ACKERMANN_CONTROLLER_HPP_

#include <mutex>
#include <string>

#include "controller_interface/controller_interface.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/subscription.hpp"
#include "rclcpp/time.hpp"

namespace fendt_ackermann_controller
{

class FendtAckermannController : public controller_interface::ControllerInterface
{
public:
  FendtAckermannController() = default;

  controller_interface::CallbackReturn on_init() override;
  controller_interface::CallbackReturn on_configure(
    const rclcpp_lifecycle::State & previous_state) override;
  controller_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;
  controller_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;

  controller_interface::InterfaceConfiguration command_interface_configuration() const override;
  controller_interface::InterfaceConfiguration state_interface_configuration() const override;

  controller_interface::return_type update(
    const rclcpp::Time & time,
    const rclcpp::Duration & period) override;

private:
  struct Cmd
  {
    double linear_x{0.0};
    double angular_z{0.0};
    rclcpp::Time stamp{0, 0, RCL_ROS_TIME};
  };

  void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg);
  static double clamp(double value, double low, double high);

  std::string cmd_vel_topic_{"/cmd_vel"};
  std::string front_left_steer_joint_;
  std::string front_right_steer_joint_;
  std::string rear_left_wheel_joint_;
  std::string rear_right_wheel_joint_;

  double wheelbase_{2.37};
  double rear_wheel_radius_{0.78};
  double max_steering_angle_{0.7853981634};
  double cmd_vel_timeout_{0.5};

  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_sub_;

  std::mutex cmd_mutex_;
  Cmd latest_cmd_;
};

}  // namespace fendt_ackermann_controller

#endif  // FENDT_ACKERMANN_CONTROLLER__FENDT_ACKERMANN_CONTROLLER_HPP_

