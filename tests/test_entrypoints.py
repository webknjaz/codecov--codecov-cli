from click.testing import CliRunner

from codecov_cli.entrypoints import UploadCollector, UploadSender, do_upload_logic
from codecov_cli.helpers.upload_sender import (
    UploadSendingResult,
    UploadSendingResultWarning,
)


def test_do_upload_logic_happy_path(mocker):
    mock_select_preparation_plugins = mocker.patch(
        "codecov_cli.entrypoints.select_preparation_plugins"
    )
    mock_select_coverage_file_finder = mocker.patch(
        "codecov_cli.entrypoints.select_coverage_file_finder"
    )
    mock_select_network_finder = mocker.patch(
        "codecov_cli.entrypoints.select_network_finder"
    )
    mock_generate_upload_data = mocker.patch.object(
        UploadCollector, "generate_upload_data"
    )
    mock_send_upload_data = mocker.patch.object(
        UploadSender,
        "send_upload_data",
        return_value=UploadSendingResult(
            error=None,
            warnings=[UploadSendingResultWarning(message="somewarningmessage")],
        ),
    )
    cli_config = {}
    versioning_system = mocker.MagicMock()
    runner = CliRunner()
    with runner.isolation() as outstreams:
        res = do_upload_logic(
            cli_config,
            versioning_system,
            commit_sha="commit_sha",
            report_code="report_code",
            build_code="build_code",
            build_url=None,
            job_code=None,
            env_vars=None,
            flags=None,
            name=None,
            network_root_folder=None,
            coverage_files_search_folder=None,
            plugin_names=["first_plugin", "another", "forth"],
            token="token",
        )
    out_bytes = outstreams[0].getvalue().decode().splitlines()
    assert out_bytes == [
        "Upload process had 1 warning",
        "Warning 1: somewarningmessage",
    ]
    assert res == UploadSender.send_upload_data.return_value
    mock_select_preparation_plugins.assert_called_with(
        cli_config, ["first_plugin", "another", "forth"]
    )
    mock_select_coverage_file_finder.assert_called_with()
    mock_select_network_finder.assert_called_with(versioning_system)
    mock_generate_upload_data.assert_called_with()
    mock_send_upload_data.assert_called_with(
        mock_generate_upload_data.return_value, "commit_sha", "token", None
    )