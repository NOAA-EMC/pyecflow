import os
from pwd import getpwuid

import pyflow as pf


scratchdir = os.path.join(os.path.abspath(''), 'scratch')
filesdir = os.path.join(scratchdir, 'files')
outdir = os.path.join(scratchdir, 'out')

if not os.path.exists(filesdir):
    os.makedirs(filesdir, exist_ok=True)

if not os.path.exists(outdir):
    os.makedirs(outdir, exist_ok=True)

passwd = getpwuid(os.getuid())

server_host = 'localhost'
server_port = 1500+passwd.pw_uid

# https://pyflow-workflow-generator.readthedocs.io/en/latest/content/introductory-course/configuring-suites.html: 

# introduce the use of a configuration object that will handle the differences, and therefore interact and configure our objects under each different context
#A configuration object can be constructed manually for different use cases or as a result of parsing configuration files. It can be used to:
# 1) Provide constants and data for specific cases, that will be needed in the suites.
# 2) Switch functionality on/off or modify it.
# 3) Configuration for hosts where to run the tasks.
# 4) Locations of and details of data to process.

# these configuration objects can be programmable in themselves (can include code). The suite components can delegate part of the suite definition to 
# these configurators and as such the structure of the suite can be determined by logic in the configuration object if necessary.

class BaseConfig:
    """This is a very contrived example showing delegation of behaviour to configuration"""

    def __init__(self, name, common_count=3, unit_count=4, integration_count=5):
        self.name = name
        self.common_count=common_count
        self.unit_count = unit_count
        self.integration_count = integration_count

    def build_unit_tests(self):
        pass

    def build_integration_tests(self):
        pass

class ProductionConfig(BaseConfig):
    def build_integration_tests(self):
        with pf.Family('integration') as f:
            pf.sequence(MyTask('integration_{}'.format(i), 123*i) for i in range(self.integration_count))
        return f

class DevConfig(BaseConfig):
    def build_unit_tests(self):
        with pf.Family('unit') as f:
            pf.sequence(MyTask('unit_{}'.format(i), 123*i) for i in range(self.unit_count))
        return f

class ConfiguredFamily(pf.Family):
    def __init__(self, config):
        super().__init__(config.name)

        with self:

            # the static part of the suite, common to all suites of this type

            with pf.Family('common') as common:
                pf.sequence(MyTask('common_{}'.format(i), 123*i) for i in range(5))

            # the dynamic part of the suite, with hooks for the variability

            test_families = [
                config.build_unit_tests(),
                config.build_integration_tests()
            ]

            # some other static of the suite

            with pf.Family('cleanup') as cleanup:
                MyTask('cleaner')

            # establish dependencies

            common >> cleanup
            for f in test_families:
                if f is not None:
                    common >> f >> cleanup
with CourseSuite('configuration_example') as s:

    ConfiguredFamily(ProductionConfig('prod', integration_count=3))

    ConfiguredFamily(DevConfig('dev', unit_count=25))


#s.check_definition()
print(s)

#s.deploy_suite()
#s.replace_on_server(server_host, server_port)
