import argparse
from load.aws_utils import AWSUtils
import configparser


def main():
    parser = argparse.ArgumentParser(description='start/stop')
    parser.add_argument('--action', type=str, help='type an action')
    args = parser.parse_args()
    action = args.action
    config = configparser.ConfigParser()
    config.read_file(open('dwh.cfg'))
    access_key = config.get('AWS', 'key')
    secret_key = config.get('AWS', 'secret')
    iam_role_name = config.get('DWH', 'DWH_IAM_ROLE_NAME')
    aws_utils_instance = AWSUtils(access_key, secret_key)

    if action == "start":
        role_arn = aws_utils_instance.create_iam_role(iam_role_name)
        dwh_endpoint = aws_utils_instance.create_redshift_cluster(role_arn)
        print('Please copy these values for future reference')
        print('DWH_ROLE_ARN={}'.format(role_arn))
        print('dwh_endpoint={}'.format(dwh_endpoint))

    elif action == "stop":
        print('destroying the cluster')
        aws_utils_instance.delete_redshift_cluster()
        print('detaching  role')
        aws_utils_instance.detach_iam_role(iam_role_name)


if __name__ == "__main__":
    main()
