#include <boost/asio.hpp>
#include <iostream>

int main (int argc, char** argv) {
    boost::asio::io_context io;
    std::cout << "test" << std::endl;
    
    return 0;
}