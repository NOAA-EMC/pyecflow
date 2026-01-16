# imports 
import pyflow as pf
from pyecflow import read_package_file, WorkflowTask, WorkflowAnchorFamily, generate_suite  # noqa: F401

# set up server
server_host = 'localhost'
server_port = 22921 #Anna's personal Ursa EcFlow server port

# Create a minimal suite for testing
with pf.Suite('testSuite', 
              host=pf.LocalHost('localhost'),
              files='./testSuite/scripts') as my_suite:
    #with pf.AnchorFamily('testFamily'):
        #with pf.Task('testTask', script='echo "test"'):
            #pass
    pass

# Generate the suite directories by importing and using the generate_suite function
generate_suite(my_suite, suite_dir='./testSuite')




"""
class WorkflowTask(pf.Task):
    def __init__(self, name: str, context: dict, **kwargs):
        super().__init__(name, variables=context['variables'], script=context['script'])

class WorkflowAnchorFamily(pf.AnchorFamily):
    def __init__(self, name: str, famAb_tasks: dict, **kwargs):
        #super().__init__(name, variables=context['variables'])
        super().__init__(name)
        task_triggers = {}
        for tt in famAb_tasks.keys(): #should a dict., keys are tasks, tt is the key 
            task_tc= famAb_tasks[tt] #get the context dict for this task
            task_triggers[tt] = WorkflowTask(tt, task_tc)
        self.task_triggers = task_triggers
"""

"""
class TestSuiteBuilder:
    #def __init__(self, filesdir, outdir, number=100):
    #    with pf.Suite('testSuite', host=pf.LocalHost('localhost'),
    #                  files=os.path.join(filesdir, 'testSuite', 'scripts'),
    #                   home=outdir, NUMBER=number) as s: #remove NUMBER?
    #def __init__(self, filesdir, outdir, number=100):
    def __init__(self, number=100):
        with pf.Suite('testSuite', host=pf.LocalHost('localhost'),
                      NUMBER=number) as s: #remove NUMBER?

            # Create family_A as parent family
            with pf.AnchorFamily('A'):
                # Create family_Aa and its tasks
                with pf.AnchorFamily('Aa'):
                    tAa1c = {'variables': {'NUMBER': number + 1}, #c is context
                             'script': "echo family_Aa NUMBER=$NUMBER"}
                    tAa1 = WorkflowTask('Aa1', tAa1c) #this will be py ecflow. context is a dict
                    #need a workflow anchor family with name of family & context. 

                # Create family_Ab and its tasks (configuration)
                famAb_tasks= {
                        'Ab1': {'variables': {'NUMBER': number + 1},
                                'script': "echo family_Ab1 NUMBER=$NUMBER"},
                        'Ab2': {'variables': {'NUMBER': number /2 },
                                'script': "echo family_Ab2 NUMBER=$NUMBER"}
                    }
                #with WorkflowAnchorFamily('Ab', famAb_tasks):
                fam = WorkflowAnchorFamily('Ab', famAb_tasks) 

                # Create task A1 directly under family A using WorkflowTask
                tA1c = {'variables': {'NUMBER': number + 1}, #c is context
                         'script': "echo family_Aa NUMBER=$NUMBER"}
                tA1 = WorkflowTask('A1', tA1c) #this will be py ecflow. context is a dict

                # Optional - Set up task dependencies within family A:
                tAa1 >> fam.task_triggers['Ab1'] >>  fam.task_triggers['Ab1']  >> tA1

            # Create family_B as parent family
            with pf.AnchorFamily('B'):
                # Create family_Ba and its tasks
                with pf.AnchorFamily('Ba'):
                    tBa1c = {'variables': {'NUMBER': number / 4}, #c is context
                             'script': "echo family_Ba1 NUMBER=$NUMBER"}
                    tBa1 = WorkflowTask('Ba1', tBa1c) #this will be py ecflow. context is a dict

                tB1c = {'variables': {'NUMBER': number / 4}, #c is context
                         'script': "echo family_B1 NUMBER=$NUMBER"}
                tB1 = WorkflowTask('B1', tB1c) #this will be py ecflow. context is a dict

        self.s = s
        #self.s.check_definition()
        #self.s.deploy_suite()
        #print(self.s)
        #print(s)
"""

"""
        # Create def directory
        def_dir = os.path.join(filesdir, 'testSuite', 'def')
        if not os.path.exists(def_dir):
            os.makedirs(def_dir, exist_ok=True)
        suite_def = self.s.ecflow_definition()
        suite_def.save_as_defs(os.path.join(def_dir, 'testSuite.def'))
        
        # Create include directory and copy header files
        include_dir = os.path.join(filesdir, 'testSuite', 'include')
        if not os.path.exists(include_dir):
            os.makedirs(include_dir, exist_ok=True)

        class Target:
            def __init__(self, filename):
                self.filename = filename
            def save(self, lines, path):
                # Use the original filename
                filepath = os.path.join(os.path.dirname(path), self.filename)
                with open(filepath, 'w') as f:
                    if isinstance(lines, list):
                        f.write('\n'.join(lines))
                    else:
                        f.write(lines)
            
        # Copy header files using their original names
        header_files = ['head.h', 'tail.h', 'envir-p1.h']
        for header_file in header_files:
            content = read_package_file('static', header_file)
            # Create a target that will save with the original filename
            target = Target(header_file)
            
            # Configure the header with the right type
            if header_file == 'tail.h':
                header = InlineCodeHeader('', content, what='tail', include_path=include_dir)
            else:
                header = InlineCodeHeader('', content, include_path=include_dir)
            header.install(target)

# Instantiate and generate the suite
builder = TestSuiteBuilder(100)
print(builder.s)

# Generate the suite using generate_suite function
generate_suite(builder.s, suite_dir='testSuite', suite_name='testSuite')
"""