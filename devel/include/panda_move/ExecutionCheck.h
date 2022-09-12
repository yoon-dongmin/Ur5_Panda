// Generated by gencpp from file panda_move/ExecutionCheck.msg
// DO NOT EDIT!


#ifndef PANDA_MOVE_MESSAGE_EXECUTIONCHECK_H
#define PANDA_MOVE_MESSAGE_EXECUTIONCHECK_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>


namespace panda_move
{
template <class ContainerAllocator>
struct ExecutionCheck_
{
  typedef ExecutionCheck_<ContainerAllocator> Type;

  ExecutionCheck_()
    : status(0)  {
    }
  ExecutionCheck_(const ContainerAllocator& _alloc)
    : status(0)  {
  (void)_alloc;
    }



   typedef int64_t _status_type;
  _status_type status;





  typedef boost::shared_ptr< ::panda_move::ExecutionCheck_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::panda_move::ExecutionCheck_<ContainerAllocator> const> ConstPtr;

}; // struct ExecutionCheck_

typedef ::panda_move::ExecutionCheck_<std::allocator<void> > ExecutionCheck;

typedef boost::shared_ptr< ::panda_move::ExecutionCheck > ExecutionCheckPtr;
typedef boost::shared_ptr< ::panda_move::ExecutionCheck const> ExecutionCheckConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::panda_move::ExecutionCheck_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::panda_move::ExecutionCheck_<ContainerAllocator> >::stream(s, "", v);
return s;
}


template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator==(const ::panda_move::ExecutionCheck_<ContainerAllocator1> & lhs, const ::panda_move::ExecutionCheck_<ContainerAllocator2> & rhs)
{
  return lhs.status == rhs.status;
}

template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator!=(const ::panda_move::ExecutionCheck_<ContainerAllocator1> & lhs, const ::panda_move::ExecutionCheck_<ContainerAllocator2> & rhs)
{
  return !(lhs == rhs);
}


} // namespace panda_move

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsFixedSize< ::panda_move::ExecutionCheck_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::panda_move::ExecutionCheck_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::panda_move::ExecutionCheck_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::panda_move::ExecutionCheck_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::panda_move::ExecutionCheck_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::panda_move::ExecutionCheck_<ContainerAllocator> const>
  : FalseType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::panda_move::ExecutionCheck_<ContainerAllocator> >
{
  static const char* value()
  {
    return "4107476a6271fc2684d94be17d33f854";
  }

  static const char* value(const ::panda_move::ExecutionCheck_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0x4107476a6271fc26ULL;
  static const uint64_t static_value2 = 0x84d94be17d33f854ULL;
};

template<class ContainerAllocator>
struct DataType< ::panda_move::ExecutionCheck_<ContainerAllocator> >
{
  static const char* value()
  {
    return "panda_move/ExecutionCheck";
  }

  static const char* value(const ::panda_move::ExecutionCheck_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::panda_move::ExecutionCheck_<ContainerAllocator> >
{
  static const char* value()
  {
    return "int64 status\n"
;
  }

  static const char* value(const ::panda_move::ExecutionCheck_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::panda_move::ExecutionCheck_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.status);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct ExecutionCheck_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::panda_move::ExecutionCheck_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::panda_move::ExecutionCheck_<ContainerAllocator>& v)
  {
    s << indent << "status: ";
    Printer<int64_t>::stream(s, indent + "  ", v.status);
  }
};

} // namespace message_operations
} // namespace ros

#endif // PANDA_MOVE_MESSAGE_EXECUTIONCHECK_H
