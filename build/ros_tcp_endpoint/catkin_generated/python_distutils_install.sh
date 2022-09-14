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

echo_and_run cd "/carrot_ws/src/ros_tcp_endpoint"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/carrot_ws/install/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/carrot_ws/install/lib/python2.7/dist-packages:/carrot_ws/build/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/carrot_ws/build" \
    "/usr/bin/python2" \
    "/carrot_ws/src/ros_tcp_endpoint/setup.py" \
    egg_info --egg-base /carrot_ws/build/ros_tcp_endpoint \
    build --build-base "/carrot_ws/build/ros_tcp_endpoint" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/carrot_ws/install" --install-scripts="/carrot_ws/install/bin"
