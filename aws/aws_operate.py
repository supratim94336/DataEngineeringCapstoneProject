import aws_utils
import argparse


def main():
    parser = argparse.ArgumentParser(description='start/stop')
    parser.add_argument('--action', type=str, help='type an action')
    args = parser.parse_args()
    action = args.action

    if action == "start":
        roleArn = aws_utils.create_iam_role()
        DWH_ENDPOINT = aws_utils.create_redshift_cluster(roleArn)
        print('Please copy these values for future reference')
        print('DWH_ROLE_ARN={}'.format(roleArn))
        print('DWH_ENDPOINT={}'.format(DWH_ENDPOINT))

    elif action == "stop":
        print('destroying the cluster')
        aws_utils.delete_redshift_cluster()
        print('detaching  role')
        aws_utils.detach_iam_role()


if __name__ == "__main__":
    main()
