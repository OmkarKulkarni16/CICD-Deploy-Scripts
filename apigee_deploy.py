import sys
import requests
import os
import zipfile
import json
import subprocess
import shutil

def clean_workspace(api_name):
    repo_dir = os.path.join(os.getcwd(), api_name)
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    print(f"Cleaned workspace for {api_name}")

def create_github_repo(api_name, github_token, github_user):
    headers = {'Authorization': f'token {github_token}'}
    data = {'name': api_name, 'private': True}
    response = requests.post(f'https://api.github.com/user/repos', headers=headers, json=data)
    response.raise_for_status()
    print(f"Repository '{api_name}' created.")
    return response.json()['html_url']

def clone_and_prepare_template(api_name, template_url):
    repo_dir = os.path.join(os.getcwd(), api_name)
    subprocess.check_call(['git', 'clone', template_url, repo_dir])
    original_file = os.path.join(repo_dir, 'apiproxy', 'dcemi-statusInquiry-v1.xml')
    new_file = os.path.join(repo_dir, 'apiproxy', f'{api_name}.xml')
    if os.path.exists(original_file):
        os.rename(original_file, new_file)
    print("Template cloned and prepared.")
    return repo_dir

def modify_xml_file(api_name, repo_dir, base_path, target_server_name, hostname, port, environment):
    xml_file = os.path.join(repo_dir, 'apiproxy', f'{api_name}.xml')
    with open(xml_file, 'r') as file:
        content = file.read()
    content = content.replace('dcemi-statusInquiry-v1', api_name)
    content = content.replace('<BasePaths>/api/v1/dcemi-statusInquiry</BasePaths>', f'<BasePaths>{base_path}</BasePaths>')
    with open(xml_file, 'w') as file:
        file.write(content)

def generate_config_json(api_name, repo_dir, base_path, target_server_name, hostname, port, environment):
    config = {
        "API_NAME": api_name,
        "BASE_PATH": base_path,
        "TARGET_SERVER_NAME": target_server_name,
        "HOSTNAME": hostname,
        "PORT": port,
        "ENVIRONMENT": environment
    }
    with open(os.path.join(repo_dir, 'config.json'), 'w') as file:
        json.dump(config, file)
    print("Config file generated.")

def zip_apiproxy(api_name, repo_dir):
    zip_path = os.path.join(repo_dir, 'apiproxy.zip')
    apiproxy_dir = os.path.join(repo_dir, 'apiproxy')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(apiproxy_dir):
            for file in files:
                full_path = os.path.join(root, file)
                zipf.write(full_path, arcname=os.path.relpath(full_path, repo_dir))
    print("apiproxy zipped.")
    return zip_path

def initialize_repo(repo_dir, github_token, repo_url):
    subprocess.check_call(['git', '-C', repo_dir, 'init'])
    subprocess.check_call(['git', '-C', repo_dir, 'remote', 'add', 'origin', repo_url])
    subprocess.check_call(['git', '-C', repo_dir, 'checkout', '-b', 'main'])
    subprocess.check_call(['git', '-C', repo_dir, 'commit', '--allow-empty', '-m', 'Initial commit'])
    subprocess.check_call(['git', '-C', repo_dir, 'push', '-u', 'origin', 'main'])
    subprocess.check_call(['git', '-C', repo_dir, 'checkout', '-b', 'develop'])
    subprocess.check_call(['git', '-C', repo_dir, 'commit', '--allow-empty', '-m', 'Initial commit for develop'])
    subprocess.check_call(['git', '-C', repo_dir, 'push', '-u', 'origin', 'develop'])

def push_to_feature_branch(repo_dir, feature_branch, commit_message):
    subprocess.check_call(['git', '-C', repo_dir, 'checkout', '-b', feature_branch])
    subprocess.check_call(['git', '-C', repo_dir, 'add', '.'])
    subprocess.check_call(['git', '-C', repo_dir, 'commit', '-m', commit_message])
    subprocess.check_call(['git', '-C', repo_dir, 'push', '-u', 'origin', feature_branch])

def extract_template(destination_dir, api_name, base_path, target_server_name, hostname, port, environment):
    # Path to JoseHigh.zip within the cloned apigee-proxy-templates repository
    zip_path = os.path.join(os.getcwd(), "apigee-proxy-templates", "templates", "JoseHigh.zip")

    # Check if the zip file exists
    if not os.path.exists(zip_path):
        print(f"Zip file not found at {zip_path}")
        return

    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
        
    # Extract the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destination_dir)
    
    print(f"Extracted {zip_path} to {destination_dir}")

    # Rename and modify XML files as necessary
    apiproxy_dir = os.path.join(destination_dir, 'apiproxy')

    # Rename XML file to match API name
    original_file = os.path.join(apiproxy_dir, 'dcemi-statusInquiry-v1.xml')
    renamed_file = os.path.join(apiproxy_dir, f'{api_name}.xml')
    if os.path.exists(original_file):
        os.rename(original_file, renamed_file)
        print(f"Renamed {original_file} to {renamed_file}")

    # Modify XML file contents with provided parameters
    with open(renamed_file, 'r') as file:
        content = file.read()
    content = content.replace('dcemi-statusInquiry-v1', api_name)
    content = content.replace('<BasePaths>/api/v1/dcemi-statusInquiry</BasePaths>', f'<BasePaths>{base_path}</BasePaths>')
    content = content.replace('<Server name="OsbseSoaUatHdfcBankCom-5142"/>', f'<Server name="{target_server_name}"/>')
    content = content.replace('http://default-host', f'http://{hostname}:{port}')
    content = content.replace('default-environment', environment)
    with open(renamed_file, 'w') as file:
        file.write(content)
    print("Updated XML configurations in the renamed file.")

# Main function to run the specified task
if __name__ == "__main__":
    task = sys.argv[1]
    
    if task == "clean_workspace":
        api_name = sys.argv[2]
        clean_workspace(api_name)
    elif task == "create_github_repo":
        api_name, github_token, github_user = sys.argv[2], sys.argv[3], sys.argv[4]
        create_github_repo(api_name, github_token, github_user)
    elif task == "clone_and_prepare_template":
        api_name, template_url = sys.argv[2], sys.argv[3]
        clone_and_prepare_template(api_name, template_url)
    elif task == "extract_template":
        api_name, base_path, target_server_name, hostname, port, environment = sys.argv[2:]
        destination_dir = os.path.join(os.getcwd(), api_name)
        extract_template(destination_dir, api_name, base_path, target_server_name, hostname, port, environment)
    elif task == "modify_xml_file":
        api_name, repo_dir, base_path, target_server_name, hostname, port, environment = sys.argv[2:]
        modify_xml_file(api_name, repo_dir, base_path, target_server_name, hostname, port, environment)
    elif task == "generate_config_json":
        api_name, repo_dir, base_path, target_server_name, hostname, port, environment = sys.argv[2:]
        generate_config_json(api_name, repo_dir, base_path, target_server_name, hostname, port, environment)
    elif task == "zip_apiproxy":
        api_name, repo_dir = sys.argv[2], sys.argv[3]
        zip_apiproxy(api_name, repo_dir)
    elif task == "initialize_repo":
        repo_dir, github_token, repo_url = sys.argv[2], sys.argv[3], sys.argv[4]
        initialize_repo(repo_dir, github_token, repo_url)
    elif task == "push_to_feature_branch":
        repo_dir, feature_branch, commit_message = sys.argv[2], sys.argv[3], sys.argv[4]
        push_to_feature_branch(repo_dir, feature_branch, commit_message)
