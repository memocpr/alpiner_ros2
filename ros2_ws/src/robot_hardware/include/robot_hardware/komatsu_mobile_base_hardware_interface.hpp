#ifndef KOMATSU_MOBILE_BASE_HARDWARE_INTERFACE_HPP
#define KOMATSU_MOBILE_BASE_HARDWARE_INTERFACE_HPP

#include "hardware_interface/system_interface.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/state.hpp"
#include <memory>
#include <cstdint>

namespace komatsu_hardware {

// Forward declaration - will be implemented in cpp
class ModbusRtuDriver;

/**
 * @brief Hardware Interface for Komatsu loader retrofit kit
 *
 * This class implements the ROS2_examples Control SystemInterface for the articulated
 * steering Komatsu loader. It interfaces with the existing retrofit kit through
 * Modbus communication (bridge_write/bridge_read).
 *
 * Responsibilities:
 * - Export state interfaces (position, velocity, steering angle)
 * - Export command interfaces (velocity, steering)
 * - Convert abstract commands to MachineSetAll messages
 * - Read machine state from MachineIndAll messages
 */
class KomatsuMobileBaseHardwareInterface : public hardware_interface::SystemInterface
{
public:
    // Lifecycle node overrides
    hardware_interface::CallbackReturn
        on_init(const hardware_interface::HardwareInfo & info) override;

    hardware_interface::CallbackReturn
        on_configure(const rclcpp_lifecycle::State & previous_state) override;

    hardware_interface::CallbackReturn
        on_activate(const rclcpp_lifecycle::State & previous_state) override;

    hardware_interface::CallbackReturn
        on_deactivate(const rclcpp_lifecycle::State & previous_state) override;

    // SystemInterface overrides
    std::vector<hardware_interface::StateInterface> export_state_interfaces() override;

    std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

    hardware_interface::return_type
        read(const rclcpp::Time & time, const rclcpp::Duration & period) override;

    hardware_interface::return_type
        write(const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
    // Modbus RTU driver for retrofit kit communication
    std::shared_ptr<ModbusRtuDriver> modbus_driver_;
    std::string modbus_port_;                          // Serial port (e.g., "/dev/ttyUSB0")
    int modbus_slave_id_;                              // Slave ID for retrofit kit

    // Hardware parameters
    double wheelbase_;              // Distance between front and rear axles
    double wheel_radius_;           // Wheel radius for velocity calculation
    double max_steering_angle_;     // Maximum steering angle (±22.4°)

    // State variables (read from MachineIndAll)
    double linear_velocity_;        // m/s
    double angular_velocity_;       // rad/s
    double steering_angle_;         // radians
    double bellcrank_angle_;        // radians (from machine feedback)
    double throttle_pedal_;         // 0.0-1.0 (actual throttle position)
    double brake_pressure_;         // bar (actual brake pressure)
    int16_t gear_state_;            // 8=forward, 9=reverse, 10=neutral

    // Command variables (to be sent as MachineSetAll)
    double cmd_throttle_;           // 0.0-1.0 (throttle command)
    double cmd_brake_;              // 0.0-1.0 (brake command)
    double cmd_steering_angle_;     // radians (converts to bellcrank degrees)
    int8_t cmd_gear_;               // 8=forward, 9=reverse, 10=neutral

    // Communication flags
    bool is_connected_;

}; // class KomatsuMobileBaseHardwareInterface

} // namespace komatsu_hardware

#endif // KOMATSU_MOBILE_BASE_HARDWARE_INTERFACE_HPP

