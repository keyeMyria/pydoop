
#include "hadoop_pipes_context.hpp"

#include <iostream>

using namespace boost::python;

//+++++++++++++++++++++++++++++++++++++++++
// Exporting class definitions.
//+++++++++++++++++++++++++++++++++++++++++
void export_hadoop_pipes_context() 
{
  using namespace boost::python;
  //--
  class_<wrap_job_conf, boost::noncopyable>("JobConf")
    .def("hasKey",      pure_virtual(&hp::JobConf::hasKey))
    .def("get",         pure_virtual(&hp::JobConf::get),
	 return_value_policy<copy_const_reference>())	 
    .def("getInt",      pure_virtual(&hp::JobConf::getInt))
    .def("getFloat",    pure_virtual(&hp::JobConf::getFloat))
    .def("getBoolean",  pure_virtual(&hp::JobConf::getBoolean))
    ;
  //--
  class_<hp::TaskContext::Counter>("TaskContext_Counter", init<int>())
    .def("getId", &hp::TaskContext::Counter::getId);
  //--
  class_<wrap_task_context, boost::noncopyable>("TaskContext")
    .def("getJobConf",  pure_virtual(&hp::TaskContext::getJobConf),
	 return_internal_reference<>())
    .def("getInputKey", pure_virtual(&hp::TaskContext::getInputKey),
	 return_value_policy<copy_const_reference>())
    .def("getInputValue", 
	 pure_virtual(&hp::TaskContext::getInputValue),
	 return_value_policy<copy_const_reference>())	 
    .def("emit",     pure_virtual(&hp::TaskContext::emit))
    .def("progress", pure_virtual(&hp::TaskContext::progress))
    .def("setStatus", pure_virtual(&hp::TaskContext::setStatus))
    .def("getCounter", pure_virtual(&hp::TaskContext::getCounter),
	 return_internal_reference<>())
    .def("incrementCounter",
	 pure_virtual(&hp::TaskContext::incrementCounter))
    ;

  //--
  class_<wrap_map_context, bases<hp::TaskContext>, 
    boost::noncopyable>("MapContext")
    .def("getJobConf",  pure_virtual(&hp::MapContext::getJobConf),
	 return_internal_reference<>())
    .def("getInputKey", pure_virtual(&hp::MapContext::getInputKey), 
	 return_value_policy<copy_const_reference>())
    .def("getInputValue", 
	 pure_virtual(&hp::MapContext::getInputValue),
	 return_value_policy<copy_const_reference>())	 
    .def("emit",     pure_virtual(&hp::MapContext::emit))
    .def("progress", pure_virtual(&hp::MapContext::progress))
    .def("setStatus", pure_virtual(&hp::MapContext::setStatus))
    .def("getCounter", pure_virtual(&hp::MapContext::getCounter),
	 return_internal_reference<>())
    .def("incrementCounter",
	 pure_virtual(&hp::MapContext::incrementCounter))
    .def("getInputKeyClass", 
	 pure_virtual(&hp::MapContext::getInputKeyClass), 
	 return_value_policy<copy_const_reference>())	 
    .def("getInputValueClass", 
	 pure_virtual(&hp::MapContext::getInputValueClass),
	 return_value_policy<copy_const_reference>())
    .def("getInputSplit", 
	 pure_virtual(&hp::MapContext::getInputSplit),
	 return_value_policy<copy_const_reference>())
    ;
  //--
  class_<wrap_reduce_context, bases<hp::TaskContext>,
    boost::noncopyable>("ReduceContext")
    .def("getJobConf",  pure_virtual(&hp::ReduceContext::getJobConf),
	 return_internal_reference<>())
    .def("getInputKey", pure_virtual(&hp::ReduceContext::getInputKey), 
	 return_value_policy<copy_const_reference>())
    .def("getInputValue", 
	 pure_virtual(&hp::ReduceContext::getInputValue),
	 return_value_policy<copy_const_reference>())
    .def("emit",     pure_virtual(&hp::ReduceContext::emit))
    .def("progress", pure_virtual(&hp::ReduceContext::progress))
    .def("setStatus", pure_virtual(&hp::ReduceContext::setStatus))
    .def("getCounter", pure_virtual(&hp::ReduceContext::getCounter),
	 return_internal_reference<>())
    .def("incrementCounter",
	 pure_virtual(&hp::ReduceContext::incrementCounter))
    .def("nextValue", 
	 pure_virtual(&hp::ReduceContext::nextValue))
    ;

}
