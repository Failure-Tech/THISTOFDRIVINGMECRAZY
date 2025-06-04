#include <boost/asio.hpp>
#include <boost/bind/bind.hpp>
#include <iomanip>
#include <sstream>
#include <iostream>

// Setting up namespace here so its easier to right out for syntax (I'm kinda lazy)
namespace asio = boost::asio;
using asio::serial_port;

class TofSensor {
    public:
        TofSensor(asio::io_context& io, const std::string& port = "COM6") // might need to change port, should be this since running off windows os?
            : serial_(io, port), timer_(io) {
                // Config of serial ports for SLCAN
                serial_.set_option(serial_port::baud_rate(1000000));
                serial_.set_option(serial_port::character_size(8));
                serial_.set_option(serial_port::stop_bits(serial_port::stop_bits::one));
                serial_.set_option(serial_port::parity(serial_port::parity::none));
                serial_.set_option(serial_port::flow_control(serial_port::flow_control::none));

                send_command("S8\r"); // Set bitrate to 1mbps
                send_command("0\r"); // opening the channel
            }

            void startMeasurements() {
                send_remote_frame(0x08); // start byte address cmd
            }

            void stopMeasurements() {
                send_remote_frame(0x09); // stop byte address cmd
            }

            // beginning an asynchronoous reading operation of data
            void asyncReadStart() {
                serial_.async_read_some(asio::buffer(read_buf_),
                    boost::bind(&TofSensor::handleRead, this,
                        asio::placeholders::error,
                        asio::placeholders:bytes_transferred));
            }

    private:
            serial_port serial_;
            asio:steady_timer timer_;
            std::array<char, 256> read_buf_; // buffer for async read
            std::string read_buffer_; // a string buffer to help accumlate the data

            // test sending a raw command string to the serial port
            void send_command(const std::string& cmd) {
                asio::write(serial_, asio::buffer(cmd.c_str(), cmd.size()));
            }

            // Sending a remote CAN frame using the SLCAN frame format
            void send_remote_frame(uint32_t can_id) {
                std::ostringstream cmd;
                cmd << "R" << std::hex << std::setw(3) << std::setfill('0') << can_id << "\r";
                send_command(cmd.str());
            }

            // Callback for when the async read does actually receive any data
            void handleRead(const boost::system::error_code& ec, size_t bytes) {
                if (!ec) {
                    read_buffer_.append(read_buf_.data(), bytes); // Appending the received bytes to the buffer
                    processBuffer(); // Parsing complete messages
                    asyncReadStart(); // continue reading more data
                }
            }

            // extracting out full CAN frames from the buffer and parsing through them
            void processBuffer() {
                size_t pos;
                while ((pos = read_buffer_.find('\r')) != std::string::npos) {
                    std::string frame = read_buffer_.substr(0, pos);
                    read_buffer_.erase(0, pos+1);

                    if (frame[0] == 'T') { // SLCAN data frame
                        parseCanFrame(frame);
                    }
                }
            }

            // Parsing a single CAN frame string and interpreting it if it is relevant
            void parseCanFrame(const std::string& frame) {
                uint32_t id;
                std::istringstream(frame.substr(1, 3)) >> std::hex >> id;

                if (id == 0x01C) { // If frame is from that address (so ToF sensor)
                    std::vector<uint8_t> data;
                    for (size_t i = 4; i < frame.size(); i+=2) {
                        uint8_t byte;
                        std::istringstream(frame.substr(i, 2)) >> std::hex >> byte;
                        data.push_back(byte);
                    }

                    if (data.size() >= 8) {
                        interpretMeasurements(data);
                    }
                }
            }

            // Pretty much the same implenetation as in the canTest.py file, just with type definitions and such
            void interpretMeasurements(const std::vector<uint8_t>& meas) {
                double distance = (meas[0] << 16 | meas[1] << 8 | meas[2]);
                distance = distance/16384.0; // scale distance

                double amplitude = (meas[3] << 8 | meas[4]);
                amplitude = amplitude/16.0; // scale ampltitude

                uint8_t signal_quality = meas[5];
                int16_t status = (meas[6] << 8 | meas[7]); // handling in signed status

                if (status >= 0x8000) {
                    status -= 0x10000;
                }

                // outputting measurement vals
                std::cout << "Distance: " << distance << std::endl << "Amplitude: " << amplitude << std::endl << "Status: " << status << std::endl;
            }
};

int main (int argc, char** argv) {
    try {
        asio::io_context io;
        TofSensor sensor(io);
        sensor.asyncReadStart(); // start reading in data
        sensor.startMeasurements(); // begin ToF measurements

        std::thread([&io]() { io.run(); }).detach(); // Run the IO
        std::this_thread::sleep_for(std::chrono::seconds(20)); // Let it run for 20s first

        sensor.stopMeasurements(); // Stop ToF readings
        io.stop(); // also stop IO
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl; // Print out any exceptions/errors
    }
    
    return 0;
}