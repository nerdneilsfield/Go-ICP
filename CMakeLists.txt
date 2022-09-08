project(GoICP)

cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

add_library(GoICPLib STATIC
	jly_goicp.cpp
	jly_3ddt.cpp
	matrix.cpp
	ConfigMap.cpp
	StringTokenizer.cpp
)

add_executable(GoICP
	jly_main.cpp
)
target_link_libraries(GoICP GoICPLib)


add_executable(GoICP_BF
  jly_brute_force.cpp
)
target_link_libraries(GoICP_BF GoICPLib)
set_target_properties(GoICP_BF PROPERTIES
  COMPILE_FLAGS "-pthread"
  LINK_FLAGS "-pthread"
  )


add_executable(GoICP_BF2
  jly_brute_force2.cpp
)
target_link_libraries(GoICP_BF2 GoICPLib)
set_target_properties(GoICP_BF2 PROPERTIES
  COMPILE_FLAGS "-pthread"
  LINK_FLAGS "-pthread"
  )
