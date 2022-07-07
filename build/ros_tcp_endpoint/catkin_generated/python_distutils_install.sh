#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/ur5_panda/src/ros_tcp_endpoint"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/ur5_panda/install/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/ur5_panda/install/lib/python2.7/dist-packages:/ur5_panda/build/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/ur5_panda/build" \
    "/usr/bin/python2" \
    "/ur5_panda/src/ros_tcp_endpoint/setup.py" \
    egg_info --egg-base /ur5_panda/build/ros_tcp_endpoint \
    build --build-base "/ur5_panda/build/ros_tcp_endpoint" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/ur5_panda/install" --install-scripts="/ur5_panda/install/bin"
