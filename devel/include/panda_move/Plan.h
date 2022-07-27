// Generated by gencpp from file panda_move/Plan.msg
// DO NOT EDIT!


#ifndef PANDA_MOVE_MESSAGE_PLAN_H
#define PANDA_MOVE_MESSAGE_PLAN_H

#include <ros/service_traits.h>


#include <panda_move/PlanRequest.h>
#include <panda_move/PlanResponse.h>


namespace panda_move
{

struct Plan
{

typedef PlanRequest Request;
typedef PlanResponse Response;
Request request;
Response response;

typedef Request RequestType;
typedef Response ResponseType;

}; // struct Plan
} // namespace panda_move


namespace ros
{
namespace service_traits
{


template<>
struct MD5Sum< ::panda_move::Plan > {
  static const char* value()
  {
    return "6b04cd40976301dcca10530fca123af6";
  }

  static const char* value(const ::panda_move::Plan&) { return value(); }
};

template<>
struct DataType< ::panda_move::Plan > {
  static const char* value()
  {
    return "panda_move/Plan";
  }

  static const char* value(const ::panda_move::Plan&) { return value(); }
};


// service_traits::MD5Sum< ::panda_move::PlanRequest> should match
// service_traits::MD5Sum< ::panda_move::Plan >
template<>
struct MD5Sum< ::panda_move::PlanRequest>
{
  static const char* value()
  {
    return MD5Sum< ::panda_move::Plan >::value();
  }
  static const char* value(const ::panda_move::PlanRequest&)
  {
    return value();
  }
};

// service_traits::DataType< ::panda_move::PlanRequest> should match
// service_traits::DataType< ::panda_move::Plan >
template<>
struct DataType< ::panda_move::PlanRequest>
{
  static const char* value()
  {
    return DataType< ::panda_move::Plan >::value();
  }
  static const char* value(const ::panda_move::PlanRequest&)
  {
    return value();
  }
};

// service_traits::MD5Sum< ::panda_move::PlanResponse> should match
// service_traits::MD5Sum< ::panda_move::Plan >
template<>
struct MD5Sum< ::panda_move::PlanResponse>
{
  static const char* value()
  {
    return MD5Sum< ::panda_move::Plan >::value();
  }
  static const char* value(const ::panda_move::PlanResponse&)
  {
    return value();
  }
};

// service_traits::DataType< ::panda_move::PlanResponse> should match
// service_traits::DataType< ::panda_move::Plan >
template<>
struct DataType< ::panda_move::PlanResponse>
{
  static const char* value()
  {
    return DataType< ::panda_move::Plan >::value();
  }
  static const char* value(const ::panda_move::PlanResponse&)
  {
    return value();
  }
};

} // namespace service_traits
} // namespace ros

#endif // PANDA_MOVE_MESSAGE_PLAN_H
