import copy
import sys
if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest
import os
import time
import json

import configuration
import session
import resource_suite


# Requires OS account 'irods' to have password 'temporarypasswordforci'
class Test_OSAuth_Only(resource_suite.ResourceBase, unittest.TestCase):

    def setUp(self):
        super(Test_OSAuth_Only, self).setUp()
        self.auth_session = session.mkuser_and_return_session('rodsuser', 'irods', 'temporarypasswordforci',
                                                          session.get_hostname())

    def tearDown(self):
        self.auth_session.__exit__()
        self.admin.assert_icommand(['iadmin', 'rmuser', self.auth_session.username])
        super(Test_OSAuth_Only, self).tearDown()

    @unittest.skipIf(configuration.TOPOLOGY_FROM_RESOURCE_SERVER, "Skip for topology testing from resource server")
    def test_authentication_OSAuth(self):
        self.auth_session.environment_file_contents['irods_authentication_scheme'] = 'OSAuth'

        # setup the irods.key file necessary for OSAuth
        keyfile_path = os.path.join(session.get_irods_config_dir(), 'irods.key')
        with open(keyfile_path, 'w') as f:
            f.write('gibberish\n')

        # do the reauth
        self.auth_session.assert_icommand('iexit full')
        self.auth_session.assert_icommand(['iinit', self.auth_session.password])
        # connect and list some files
        self.auth_session.assert_icommand('icd')
        self.auth_session.assert_icommand('ils -L', 'STDOUT_SINGLELINE', 'home')

        # reset client environment to original
        del self.auth_session.environment_file_contents['irods_authentication_scheme']

        # clean up keyfile
        os.unlink(keyfile_path)

# Requires existence of OS account 'irodsauthuser' with password 'iamnotasecret'


class Test_Auth(resource_suite.ResourceBase, unittest.TestCase):
    def setUp(self):
        super(Test_Auth, self).setUp()
        cfg_file = os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/test_framework_configuration.json')
        with open(cfg_file,'r') as f:
            cfg = json.load(f)
            auth_user = cfg['irods_authuser_name']
            auth_pass = cfg['irods_authuser_password']
            self.auth_session = session.mkuser_and_return_session('rodsuser', auth_user, auth_pass, session.get_hostname())

    def tearDown(self):
        self.auth_session.__exit__()
        self.admin.assert_icommand(['iadmin', 'rmuser', self.auth_session.username])
        super(Test_Auth, self).tearDown()

    @unittest.skipIf(configuration.TOPOLOGY_FROM_RESOURCE_SERVER or configuration.USE_SSL, 'Topo from resource or SSL')
    def test_authentication_PAM_without_negotiation(self):
        session.run_command('openssl genrsa -out server.key')
        session.run_command('openssl req -batch -new -key server.key -out server.csr')
        session.run_command('openssl req -batch -new -x509 -key server.key -out chain.pem -days 365')
        session.run_command('openssl dhparam -2 -out dhparams.pem 1024')  # normally 2048, but smaller size here for speed

        service_account_environment_file_path = os.path.expanduser('~/.irods/irods_environment.json')
        with session.file_backed_up(service_account_environment_file_path):
            server_update = {
                'irods_ssl_certificate_chain_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/chain.pem'),
                'irods_ssl_certificate_key_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/server.key'),
                'irods_ssl_dh_params_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/dhparams.pem'),
                'irods_ssl_verify_server': 'none',
            }
            session.update_json_file_from_dict(service_account_environment_file_path, server_update)

            client_update = {
                'irods_ssl_certificate_chain_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/chain.pem'),
                'irods_ssl_certificate_key_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/server.key'),
                'irods_ssl_dh_params_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/dhparams.pem'),
                'irods_ssl_verify_server': 'none',
                'irods_authentication_scheme': 'PaM',
            }

            # now the actual test
            auth_session_env_backup = copy.deepcopy(self.auth_session.environment_file_contents)
            self.auth_session.environment_file_contents.update(client_update)

            # server reboot to pick up new irodsEnv settings
            session.restart_irods_server()

            # do the reauth
            self.auth_session.assert_icommand(['iinit', self.auth_session.password])
            # connect and list some files
            self.auth_session.assert_icommand('icd')
            self.auth_session.assert_icommand('ils -L', 'STDOUT_SINGLELINE', 'home')

            # reset client environment to original
            self.auth_session.environment_file_contents = auth_session_env_backup

            # clean up
            for file in ['tests/pydevtest/server.key', 'tests/pydevtest/chain.pem', 'tests/pydevtest/dhparams.pem']:
                os.unlink(os.path.join(session.get_irods_top_level_dir(), file))

        # server reboot to pick up new irodsEnv and server settings
        session.restart_irods_server()

    @unittest.skipIf(configuration.TOPOLOGY_FROM_RESOURCE_SERVER or configuration.USE_SSL, 'Topo from resource or SSL')
    def test_authentication_PAM_with_server_params(self):
        session.run_command('openssl genrsa -out server.key')
        session.run_command('openssl req -batch -new -key server.key -out server.csr')
        session.run_command('openssl req -batch -new -x509 -key server.key -out chain.pem -days 365')
        session.run_command('openssl dhparam -2 -out dhparams.pem 1024')  # normally 2048, but smaller size here for speed

        service_account_environment_file_path = os.path.expanduser('~/.irods/irods_environment.json')
        with session.file_backed_up(service_account_environment_file_path):
            server_update = {
                'irods_ssl_certificate_chain_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/chain.pem'),
                'irods_ssl_certificate_key_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/server.key'),
                'irods_ssl_dh_params_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/dhparams.pem'),
                'irods_ssl_verify_server': 'none',
            }
            session.update_json_file_from_dict(service_account_environment_file_path, server_update)

            client_update = {
                'irods_ssl_certificate_chain_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/chain.pem'),
                'irods_ssl_certificate_key_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/server.key'),
                'irods_ssl_dh_params_file': os.path.join(session.get_irods_top_level_dir(), 'tests/pydevtest/dhparams.pem'),
                'irods_ssl_verify_server': 'none',
                'irods_authentication_scheme': 'PaM',
                'irods_client_server_policy': 'CS_NEG_REQUIRE',
            }

            auth_session_env_backup = copy.deepcopy(self.auth_session.environment_file_contents)
            self.auth_session.environment_file_contents.update(client_update)

            server_config_filename = session.get_irods_config_dir() + '/server_config.json'
            with session.file_backed_up(server_config_filename):
                server_config_update = {
                    'pam_password_length': 20,
                    'pam_no_extend': False,
                    'pam_password_min_time': 121,
                    'pam_password_max_time': 1209600,
                }
                session.update_json_file_from_dict(server_config_filename, server_config_update)

                session.restart_irods_server()

                # the test
                self.auth_session.assert_icommand(['iinit', self.auth_session.password])
                self.auth_session.assert_icommand("icd")
                self.auth_session.assert_icommand("ils -L", 'STDOUT_SINGLELINE', "home")

        self.auth_session.environment_file_contents = auth_session_env_backup
        for file in ['tests/pydevtest/server.key', 'tests/pydevtest/chain.pem', 'tests/pydevtest/dhparams.pem']:
            os.unlink(os.path.join(session.get_irods_top_level_dir(), file))

        session.restart_irods_server()

    def test_iinit_repaving_2646(self):
        initial_contents = copy.deepcopy(self.admin.environment_file_contents)
        del self.admin.environment_file_contents['irods_zone_name']
        self.admin.run_icommand('iinit', stdin_string='{0}\n{1}\n'.format(initial_contents['irods_zone_name'], self.admin.password))
        final_contents = session.open_and_load_json_ascii(os.path.join(self.admin.local_session_dir, 'irods_environment.json'))
        self.admin.environment_file_contents = initial_contents
        print initial_contents
        print final_contents
        assert initial_contents == final_contents