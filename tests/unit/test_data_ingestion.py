from data_ingestion.fetcher import fetch_rounds, process_rounds
from unittest.mock import patch

@patch('data_ingestion.fetcher.httpx.get')
def test_fetch_rounds_success(mock_get, test_session):
    mock_response = {
        "success": True,
        "data": {
            "list": [
                {"issueNumber": "20230729001", "winningNumber": 5, "drawTime": "2023-07-29 00:00:00"},
                {"issueNumber": "20230729000", "winningNumber": 3, "drawTime": "2023-07-28 23:59:30"}
            ]
        }
    }
    mock_get.return_value.json.return_value = mock_response
    
    rounds = fetch_rounds()
    assert len(rounds) == 2
    assert rounds[0]['issueNumber'] == "20230729001"

def test_process_rounds(test_session, sample_data):
    test_data = [
        {"issueNumber": "20230729002", "winningNumber": 7, "drawTime": "2023-07-29 00:00:30"},
        {"issueNumber": "20230729003", "winningNumber": 2, "drawTime": "2023-07-29 00:01:00"}
    ]
    
    # Mock the fetch_rounds function
    with patch('data_ingestion.fetcher.fetch_rounds', return_value=test_data):
        process_rounds(test_session)
        
        # Check if new rounds were added
        count = test_session.query(WingoRound).count()
        assert count == 502  # 500 sample + 2 new