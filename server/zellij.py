import subprocess


def send_input(session: str, text: str) -> None:
    subprocess.run(
        ["zellij", "--session", session, "action", "write-chars", text],
        check=True,
        capture_output=True,
    )


def send_enter(session: str) -> None:
    # byte 10 = newline / Enter
    subprocess.run(
        ["zellij", "--session", session, "action", "write", "10"],
        check=True,
        capture_output=True,
    )


def send_message(session: str, text: str) -> None:
    send_input(session, text)
    send_enter(session)
