import base64
import datetime
import json
import logging
import os

import nacl.public
import requests
from IPython.core.interactiveshell import ExecutionInfo
from requests import Response
from requests.auth import HTTPBasicAuth

logging.basicConfig(filename=".output.log", level=logging.INFO, force=True)


def telemetry(info: ExecutionInfo) -> None:
    cell_content = info.raw_cell
    log_encrypted(f"code run: {cell_content}")


def encrypt_to_b64(message: str) -> str:
    with open("server_public_key.bin", "rb") as f:
        server_pub_key_bytes = f.read()
    server_pub_key = nacl.public.PublicKey(server_pub_key_bytes)

    with open("client_private_key.bin", "rb") as f:
        client_private_key_bytes = f.read()
    client_priv_key = nacl.public.PrivateKey(client_private_key_bytes)

    box = nacl.public.Box(client_priv_key, server_pub_key)
    encrypted = box.encrypt(message.encode())
    encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")

    return encrypted_b64


def log_encrypted(message: str) -> None:
    encrypted_b64 = encrypt_to_b64(message)
    logging.info(f"Encrypted Output: {encrypted_b64}")


def log_variable(value, info_type) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"{info_type}, {value}, {timestamp}"
    log_encrypted(message)


def ensure_responses() -> dict:
    with open(".responses.json", "a") as _:
        pass

    data = {}

    try:
        with open(".responses.json", "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        with open(".responses.json", "w") as f:
            json.dump(data, f)

    return data


def update_responses(key: str, value) -> dict:
    data = ensure_responses()
    data[key] = value

    temp_path = ".responses.tmp"
    orig_path = ".responses.json"

    try:
        with open(temp_path, "w") as f:
            json.dump(data, f)

        os.replace(temp_path, orig_path)
    except (TypeError, json.JSONDecodeError) as e:
        print(f"Failed to update responses: {e}")

        if os.path.exists(temp_path):
            os.remove(temp_path)

        raise

    return data


def score_question(
    student_email: str,
    term: str,
    assignment: str,
    question: str,
    submission: str,
    base_url: str = "http://localhost:8000",
) -> Response:
    url = base_url + "/live-scorer"

    payload = {
        "student_email": student_email,
        "term": term,
        "assignment": assignment,
        "question": question,
        "responses": submission,
    }

    res = requests.post(url, json=payload, auth=HTTPBasicAuth("student", "capture"))

    return res


def submit_question_new(
    student_email: str,
    term: str,
    assignment: str,
    question: str,
    responses: dict,
    score: dict,
    base_url: str = "http://localhost:8000",
):
    url = base_url + "/submit-question"

    payload = {
        "student_email": student_email,
        "term": term,
        "assignment": assignment,
        "question": question,
        "responses": responses,
        "score": score,
    }

    res = requests.post(url, json=payload, auth=HTTPBasicAuth("student", "capture"))

    return res
