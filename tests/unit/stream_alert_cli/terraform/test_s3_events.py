"""
Copyright 2017-present, Airbnb Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from mock import patch
from nose.tools import assert_equal, assert_false, assert_true

from stream_alert_cli.config import CLIConfig
from stream_alert_cli.terraform import _common, s3_events

CONFIG = CLIConfig(config_path='tests/unit/conf')


def test_generate_s3_events_legacy():
    """CLI - Terraform S3 Events - Legacy"""
    cluster_dict = _common.infinitedict()
    CONFIG['clusters']['test']['modules']['s3_events'] = {
        's3_bucket_id': 'unit-test-bucket.legacy.data'
    }
    result = s3_events.generate_s3_events('test', cluster_dict, CONFIG)
    # Reload the config
    CONFIG.load()

    assert_true(result)
    assert_equal(CONFIG['clusters']['test']['modules']['s3_events'],
                 [{
                     'bucket_id': 'unit-test-bucket.legacy.data'
                 }])


def test_generate_s3_events():
    """CLI - Terraform S3 Events with Valid Buckets"""
    cluster_dict = _common.infinitedict()
    result = s3_events.generate_s3_events('advanced', cluster_dict, CONFIG)

    expected_config = {
        'module': {
            's3_events_unit-test-bucket_data': {
                'source': 'modules/tf_stream_alert_s3_events',
                'lambda_function_arn': '${module.stream_alert_advanced.lambda_arn}',
                'bucket_id': 'unit-test-bucket.data',
                'enable_events': True,
                'lambda_role_id': '${module.stream_alert_advanced.lambda_role_id}',
            },
            's3_events_unit-test_cloudtrail_data': {
                'source': 'modules/tf_stream_alert_s3_events',
                'lambda_function_arn': '${module.stream_alert_advanced.lambda_arn}',
                'bucket_id': 'unit-test.cloudtrail.data',
                'enable_events': False,
                'lambda_role_id': '${module.stream_alert_advanced.lambda_role_id}',
            }
        }
    }

    assert_true(result)
    assert_equal(cluster_dict, expected_config)


@patch('stream_alert_cli.terraform.s3_events.LOGGER_CLI')
def test_generate_s3_events_invalid_bucket(mock_logging):
    """CLI - Terraform S3 Events with Missing Bucket Key"""
    cluster_dict = _common.infinitedict()
    CONFIG['clusters']['advanced']['modules']['s3_events'] = [{'wrong_key': 'my-bucket!!!'}]
    result = s3_events.generate_s3_events('advanced', cluster_dict, CONFIG)

    assert_true(mock_logging.error.called)
    assert_false(result)
