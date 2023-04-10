#!/usr/bin/env python3

from typing import Union, List, Tuple
from pathlib import Path
import os
import subprocess
import shlex
import shutil

DEFAULT_INSTALL_PATH = Path(os.environ["HOME"]) / "OpenFace"
DEFAULT_PROFILE_PATH = Path(os.environ["HOME"]) / ".bashrc"

REPOSITORY_URL = "https://github.com/GuillaumeRochette/OpenFace"
LICENSE_URL = "https://github.com/TadasBaltrusaitis/OpenFace/blob/master/OpenFace-license.txt"


def wrap(commands: Union[List[str], Tuple[str, ...]], sep: str = " && ") -> str:
    start = 'bash -c "'
    end = '"'
    return start + sep.join(commands) + end


def main():
    print("Welcome to the OpenFace Python install script.")
    print("This is a fork of OpenFace, developed and maintained by Tadas Baltrusaitis.")
    print("In order to continue the installation process, please review the license")
    print(f"agreement at: {LICENSE_URL}.")
    print("You must comply with this license agreement, e.g. academic, research or")
    print("non-commercial purposes, to proceed with the installation.")
    print("Do you accept the license terms?")
    ans = input("[yes|no] >>> ").lower()
    while ans not in ["yes", "no"]:
        ans = input("Please answer 'yes' or 'no' >>>").lower()
    license_accepted = ans == "yes"
    if not license_accepted:
        print("The license agreement wasn't approved, aborting installation.")
        exit(1)

    print(f"OpenFace will now be installed into this location:")
    print(DEFAULT_INSTALL_PATH)
    print("\t- Press ENTER to confirm the location.")
    print("\t- Or specify a different location below.")
    ans = input(">>> ")
    if not ans:
        install_path = DEFAULT_INSTALL_PATH
    else:
        install_path = Path(ans).resolve(strict=False)

    if install_path.exists():
        raise FileExistsError(install_path)
    install_path.parent.mkdir(parents=True, exist_ok=True)

    print("Be patient, the installation may take a while.")
    subprocess.run(
        args=shlex.split(
            wrap(
                [
                    f"git clone {REPOSITORY_URL} {install_path}",
                    f"cd {install_path}",
                    "./download_models.sh",
                    "./install.sh",
                ]
            )
        ),
        check=True,
    )
    print("Installation successful.")

    print("Do you want to keep the installation minimal, that is to remove everything")
    print("but the binaries and the models, to save space?")
    print("If not, the whole repository, which is quite voluminous, will be kept as is.")
    ans = input("[yes|no] >>> ").lower()
    while ans not in ["yes", "no"]:
        ans = input("Please answer 'yes' or 'no' >>>").lower()
    minimal_installation = ans == "yes"

    if minimal_installation:
        for p in install_path.glob("*"):
            if p.is_dir() and p.name != "build":
                shutil.rmtree(p)
            elif p.is_file():
                p.unlink()
        for p in (install_path / "build").glob("*"):
            if p.is_dir() and p.name != "bin":
                shutil.rmtree(p)
            elif p.is_file():
                p.unlink()

    path_cmd = f'export PATH="{install_path}/build/bin:$PATH"'

    print("Do you wish to add OpenFace to the PATH environment variable automatically?")
    print("If so, the following line will be added in a file read by your login shell:")
    print(path_cmd)
    print("Otherwise, you will have to manually add it yourself.")
    ans = input("[yes|no] >>> ").lower()
    while ans not in ["yes", "no"]:
        ans = input("Please answer 'yes' or 'no' >>>").lower()
    add_to_login_shell = ans == "yes"

    if add_to_login_shell:
        print(f"The line will be appended to {DEFAULT_PROFILE_PATH}:")
        print("\t- Press ENTER to confirm the location.")
        print("\t- Or specify a different location below.")
        ans = input(">>> ")
        if not ans:
            profile_path = DEFAULT_PROFILE_PATH
        else:
            profile_path = Path(ans).resolve(strict=False)

        with profile_path.open("a") as file:
            print(path_cmd, file=file, flush=True)
            print("", file=file, flush=True)


if __name__ == "__main__":
    main()
