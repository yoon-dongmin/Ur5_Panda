// Generated by gencpp from file panda_move/InitRequest.msg
// DO NOT EDIT!


#ifndef PANDA_MOVE_MESSAGE_INITREQUEST_H
#define PANDA_MOVE_MESSAGE_INITREQUEST_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>

#include <geometry_msgs/Point.h>
#include <geometry_msgs/Quaternion.h>
#include <geometry_msgs/Vector3.h>

namespace panda_move
{
template <class ContainerAllocator>
struct InitRequest_
{
  typedef InitRequest_<ContainerAllocator> Type;

  InitRequest_()
    : activated_object()
    , position()
    , orientation()
    , scale()
    , joint_state()  {
    }
  InitRequest_(const ContainerAllocator& _alloc)
    : activated_object(_alloc)
    , position(_alloc)
    , orientation(_alloc)
    , scale(_alloc)
    , joint_state(_alloc)  {
  (void)_alloc;
    }



   typedef std::vector<std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other > , typename ContainerAllocator::template rebind<std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other > >::other >  _activated_object_type;
  _activated_object_type activated_object;

   typedef std::vector< ::geometry_msgs::Point_<ContainerAllocator> , typename ContainerAllocator::template rebind< ::geometry_msgs::Point_<ContainerAllocator> >::other >  _position_type;
  _position_type position;

   typedef std::vector< ::geometry_msgs::Quaternion_<ContainerAllocator> , typename ContainerAllocator::template rebind< ::geometry_msgs::Quaternion_<ContainerAllocator> >::other >  _orientation_type;
  _orientation_type orientation;

   typedef std::vector< ::geometry_msgs::Vector3_<ContainerAllocator> , typename ContainerAllocator::template rebind< ::geometry_msgs::Vector3_<ContainerAllocator> >::other >  _scale_type;
  _scale_type scale;

   typedef std::vector<double, typename ContainerAllocator::template rebind<double>::other >  _joint_state_type;
  _joint_state_type joint_state;





  typedef boost::shared_ptr< ::panda_move::InitRequest_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::panda_move::InitRequest_<ContainerAllocator> const> ConstPtr;

}; // struct InitRequest_

typedef ::panda_move::InitRequest_<std::allocator<void> > InitRequest;

typedef boost::shared_ptr< ::panda_move::InitRequest > InitRequestPtr;
typedef boost::shared_ptr< ::panda_move::InitRequest const> InitRequestConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::panda_move::InitRequest_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::panda_move::InitRequest_<ContainerAllocator> >::stream(s, "", v);
return s;
}


template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator==(const ::panda_move::InitRequest_<ContainerAllocator1> & lhs, const ::panda_move::InitRequest_<ContainerAllocator2> & rhs)
{
  return lhs.activated_object == rhs.activated_object &&
    lhs.position == rhs.position &&
    lhs.orientation == rhs.orientation &&
    lhs.scale == rhs.scale &&
    lhs.joint_state == rhs.joint_state;
}

template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator!=(const ::panda_move::InitRequest_<ContainerAllocator1> & lhs, const ::panda_move::InitRequest_<ContainerAllocator2> & rhs)
{
  return !(lhs == rhs);
}


} // namespace panda_move

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsFixedSize< ::panda_move::InitRequest_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::panda_move::InitRequest_<ContainerAllocator> const>
  : FalseType
  { };

template <class ContainerAllocator>
struct IsMessage< ::panda_move::InitRequest_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::panda_move::InitRequest_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::panda_move::InitRequest_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::panda_move::InitRequest_<ContainerAllocator> const>
  : FalseType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::panda_move::InitRequest_<ContainerAllocator> >
{
  static const char* value()
  {
    return "3ddc831ca2bee40010e5808350701489";
  }

  static const char* value(const ::panda_move::InitRequest_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0x3ddc831ca2bee400ULL;
  static const uint64_t static_value2 = 0x10e5808350701489ULL;
};

template<class ContainerAllocator>
struct DataType< ::panda_move::InitRequest_<ContainerAllocator> >
{
  static const char* value()
  {
    return "panda_move/InitRequest";
  }

  static const char* value(const ::panda_move::InitRequest_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::panda_move::InitRequest_<ContainerAllocator> >
{
  static const char* value()
  {
    return "string[] activated_object\n"
"geometry_msgs/Point[] position\n"
"geometry_msgs/Quaternion[] orientation\n"
"geometry_msgs/Vector3[] scale\n"
"float64[] joint_state\n"
"\n"
"================================================================================\n"
"MSG: geometry_msgs/Point\n"
"# This contains the position of a point in free space\n"
"float64 x\n"
"float64 y\n"
"float64 z\n"
"\n"
"================================================================================\n"
"MSG: geometry_msgs/Quaternion\n"
"# This represents an orientation in free space in quaternion form.\n"
"\n"
"float64 x\n"
"float64 y\n"
"float64 z\n"
"float64 w\n"
"\n"
"================================================================================\n"
"MSG: geometry_msgs/Vector3\n"
"# This represents a vector in free space. \n"
"# It is only meant to represent a direction. Therefore, it does not\n"
"# make sense to apply a translation to it (e.g., when applying a \n"
"# generic rigid transformation to a Vector3, tf2 will only apply the\n"
"# rotation). If you want your data to be translatable too, use the\n"
"# geometry_msgs/Point message instead.\n"
"\n"
"float64 x\n"
"float64 y\n"
"float64 z\n"
;
  }

  static const char* value(const ::panda_move::InitRequest_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::panda_move::InitRequest_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.activated_object);
      stream.next(m.position);
      stream.next(m.orientation);
      stream.next(m.scale);
      stream.next(m.joint_state);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct InitRequest_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::panda_move::InitRequest_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::panda_move::InitRequest_<ContainerAllocator>& v)
  {
    s << indent << "activated_object[]" << std::endl;
    for (size_t i = 0; i < v.activated_object.size(); ++i)
    {
      s << indent << "  activated_object[" << i << "]: ";
      Printer<std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other > >::stream(s, indent + "  ", v.activated_object[i]);
    }
    s << indent << "position[]" << std::endl;
    for (size_t i = 0; i < v.position.size(); ++i)
    {
      s << indent << "  position[" << i << "]: ";
      s << std::endl;
      s << indent;
      Printer< ::geometry_msgs::Point_<ContainerAllocator> >::stream(s, indent + "    ", v.position[i]);
    }
    s << indent << "orientation[]" << std::endl;
    for (size_t i = 0; i < v.orientation.size(); ++i)
    {
      s << indent << "  orientation[" << i << "]: ";
      s << std::endl;
      s << indent;
      Printer< ::geometry_msgs::Quaternion_<ContainerAllocator> >::stream(s, indent + "    ", v.orientation[i]);
    }
    s << indent << "scale[]" << std::endl;
    for (size_t i = 0; i < v.scale.size(); ++i)
    {
      s << indent << "  scale[" << i << "]: ";
      s << std::endl;
      s << indent;
      Printer< ::geometry_msgs::Vector3_<ContainerAllocator> >::stream(s, indent + "    ", v.scale[i]);
    }
    s << indent << "joint_state[]" << std::endl;
    for (size_t i = 0; i < v.joint_state.size(); ++i)
    {
      s << indent << "  joint_state[" << i << "]: ";
      Printer<double>::stream(s, indent + "  ", v.joint_state[i]);
    }
  }
};

} // namespace message_operations
} // namespace ros

#endif // PANDA_MOVE_MESSAGE_INITREQUEST_H