import os
import subprocess

def git_pull():
    # Navigate to root dir
    
    # os.chdir('/TravelMaster/ui/react-ui>')

    # pull changes from git master
    subprocess.run(['git', 'pull'])

def git_add_commit():
    # Add all changes
    subprocess.run(['git', 'add', '.'])

    #commit the changes
    commit_msg = input("Enter commit msg:")

    subprocess.run(['git', 'commit', '-m', commit_msg])

def navigate_and_build():
    # navigate to ui>>>react-ui
    
    # os.chdir('ui')
    # os.chdir('react-ui')

    package_name = input("Enter package name:")

    if package_name:
        subprocess.run(['npm', 'install', package_name])
    
    # build the app
    subprocess.run(['npm', 'build'])


if __name__ == "__main__":
    git_pull()
    git_add_commit()
    navigate_and_build()






