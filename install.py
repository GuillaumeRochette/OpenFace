#!/usr/bin/env python3

from typing import Union, List, Tuple

from pathlib import Path
import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--license_accepted", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--install_path", type=Path, default=None)
    parser.add_argument("--overwrite_install", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--minimal_install", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--add_to_login_shell", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--profile_path", type=Path, default=None)
    parser.add_argument("--silent_install", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    if args.silent_install:
        args.license_accepted = True
        args.install_path = DEFAULT_INSTALL_PATH
        args.overwrite_install = True
        args.minimal_install = True
        args.add_to_login_shell = True
        args.profile_path = DEFAULT_PROFILE_PATH
    
    print("Welcome to the OpenFace Python install script.")
    print("This is a fork of OpenFace, developed and maintained by Tadas Baltrusaitis.")
    print("In order to continue the install process, please review the license")
    print(f"agreement at: {LICENSE_URL}.")
    print("You must comply with this license agreement, e.g. academic, research or")
    print("non-commercial purposes, to proceed with the install.")
    print("Do you accept the license terms?")

    if args.license_accepted is None:
        ans = input("[yes|no] >>> ").lower()
        while ans not in ["yes", "no"]:
            ans = input("Please answer 'yes' or 'no' >>>").lower()
        args.license_accepted = ans == "yes"
    
    if args.license_accepted:
        print("Yes, I do accept the license terms.")
    else:
        print("No, I do not accept the license terms.")
        print("Aborting install.")
        raise ValueError(args.license_accepted)

    if args.install_path is None:
        print(f"The default install path is:")
        print(DEFAULT_INSTALL_PATH)
        print("\t- Press ENTER to confirm the location.")
        print("\t- Or specify a different location below.")
        ans = input(">>> ")
        if not ans:
            args.install_path = DEFAULT_INSTALL_PATH
        else:
            args.install_path = Path(ans).resolve(strict=False)

    if args.install_path.exists():
        if args.overwrite_install:
            shutil.rmtree(args.install_path)
        else:
            raise FileExistsError(args.install_path)
    args.install_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"OpenFace will now be installed into this location:")
    print(args.install_path)
    print("Be patient, the install may take a while.")
    subprocess.run(
        args=shlex.split(
            wrap(
                [
                    f"git clone {REPOSITORY_URL} {args.install_path}",
                    f"cd {args.install_path}",
                    "./download_models.sh",
                    "./install.sh",
                ]
            )
        ),
        check=True,
    )
    print("Install successful.")

    print("Do you want to keep the install minimal, that is to remove everything")
    print("but the binaries and the models, to save space?")
    print("If not, the whole repository, which is quite voluminous, will be kept as is.")

    if args.minimal_install is None:
        ans = input("[yes|no] >>> ").lower()
        while ans not in ["yes", "no"]:
            ans = input("Please answer 'yes' or 'no' >>>").lower()
        args.minimal_install = ans == "yes"

    if args.minimal_install:
        print("Yes, I want the install to be minimal.")
        for p in args.install_path.glob("*"):
            if p.is_dir() and p.name != "build":
                shutil.rmtree(p)
            elif p.is_file():
                p.unlink()
        for p in (args.install_path / "build").glob("*"):
            if p.is_dir() and p.name != "bin":
                shutil.rmtree(p)
            elif p.is_file():
                p.unlink()
    else:
        print("No, I want the install to be kept as is.")

    path_cmd = f'export PATH="{args.install_path}/build/bin:$PATH"'

    print("OpenFace can be added to the PATH environment variable automatically.")
    print("If you want to, the following line will be added in a file read by your login shell:")
    print(path_cmd)
    print("Otherwise, you will have to manually add it yourself.")

    if args.add_to_login_shell:
        print("Do you wish to add OpenFace to the PATH environment variable automatically?")
        ans = input("[yes|no] >>> ").lower()
        while ans not in ["yes", "no"]:
            ans = input("Please answer 'yes' or 'no' >>>").lower()
        args.add_to_login_shell = ans == "yes"

    if args.add_to_login_shell:
        print("Yes, I want to have it added automatically.")
        if args.profile_path is None:
            print(f"The line will be appended to {DEFAULT_PROFILE_PATH}:")
            print("\t- Press ENTER to confirm the location.")
            print("\t- Or specify a different location below.")
            ans = input(">>> ")
            if not ans:
                args.profile_path = DEFAULT_PROFILE_PATH
            else:
                args.profile_path = Path(ans).resolve(strict=False)
        else:
            print(f"The line will be appended to {args.profile_path}.")

        with args.profile_path.open("a") as file:
            print(path_cmd, file=file, flush=True)
            print("", file=file, flush=True)
    else:
        print("No, I do not want to have it added automatically.")


if __name__ == "__main__":
    main()
