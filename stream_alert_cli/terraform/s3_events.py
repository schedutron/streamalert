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
from stream_alert_cli.logger import LOGGER_CLI


def generate_s3_events(cluster_name, cluster_dict, config):
    """Add the S3 Events module to the Terraform cluster dict.

    Args:
        cluster_name (str): The name of the currently generating cluster
        cluster_dict (defaultdict): The dict containing all Terraform config for a given cluster.
        config (dict): The loaded config from the 'conf/' directory

    Returns:
        bool: Result of applying the s3_events module
    """
    modules = config['clusters'][cluster_name]['modules']
    s3_event_buckets = modules['s3_events']

    # Detect legacy and convert
    if isinstance(s3_event_buckets, dict) and 's3_bucket_id' in s3_event_buckets:
        del config['clusters'][cluster_name]['modules']['s3_events']
        s3_event_buckets = [{'bucket_id': s3_event_buckets['s3_bucket_id']}]
        config['clusters'][cluster_name]['modules']['s3_events'] = s3_event_buckets
        LOGGER_CLI.info('Converting legacy S3 Events config')
        config.write()

    for bucket_info in s3_event_buckets:
        if 'bucket_id' not in bucket_info:
            LOGGER_CLI.error('Config Error: Missing bucket_id key from s3_event configuration')
            return False

        cluster_dict['module']['s3_events_{}'.format(bucket_info['bucket_id'].replace(
            '.', '_'))] = {
                'source': 'modules/tf_stream_alert_s3_events',
                'lambda_function_arn':
                '${{module.stream_alert_{}.lambda_arn}}'.format(cluster_name),
                'bucket_id': bucket_info['bucket_id'],
                'enable_events': bucket_info.get('enable_events', True),
                'lambda_role_id': '${{module.stream_alert_{}.lambda_role_id}}'.format(cluster_name)
            }

    return True
