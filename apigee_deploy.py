import sys
import requests
import os
import zipfile
import git
import json

# Define each task as a function

def create_github_repo(api_name, github_token, github_user):
    headers = {'Authorization': f'token {github_token}'}
    data = {'name': api_name, 'private': True}
    response = requests.post(f'https://api.github.com/user/repos', headers=headers, json=data)
    response.raise_for_status()
    print(f"Repository '{api_name}' created.")
    return response.json()['html_url']

def clone_and_prepare_template(api_name, template_url):
    repo_dir = os.path.join(os.getcwd(), api_name)
    git.Repo.clone_from(template_url, repo_dir, branch='main')
    os.rename(os.path.join(repo_dir, 'apiproxy', 'dcemi-statusInquiry-v1.xml'), os.path.join(repo_dir, 'apiproxy', f'{api_name}.xml'))
    print("Template cloned and prepared.")
    return repo_dir

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

# Main function to run the specified task
if __name__ == "__main__":
    task = sys.argv[1]
    if task == "create_github_repo":
        api_name, github_token, github_user = sys.argv[2], sys.argv[3], sys.argv[4]
        create_github_repo(api_name, github_token, github_user)
    elif task == "clone_and_prepare_template":
        api_name, template_url = sys.argv[2], sys.argv[3]
        clone_and_prepare_template(api_name, template_url)
    elif task == "generate_config_json":
        api_name, repo_dir, base_path, target_server_name, hostname, port, environment = sys.argv[2:]
        generate_config_json(api_name, repo_dir, base_path, target_server_name, hostname, port, environment)
    elif task == "zip_apiproxy":
        api_name, repo_dir = sys.argv[2], sys.argv[3]
        zip_apiproxy(api_name, repo_dir)
