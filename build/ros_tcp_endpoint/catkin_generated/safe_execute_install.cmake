execute_process(COMMAND "/ur5_panda/build/ros_tcp_endpoint/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/ur5_panda/build/ros_tcp_endpoint/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
