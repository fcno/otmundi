from apps.engine.killstats.ingestion.providers.killstats_scraper import (
    KillStatsScraperProvider,
    RawProviderInput,
)


def test_normalize_raw_full_structure() -> None:
    provider = KillStatsScraperProvider()

    raw: RawProviderInput = {
        "snapshot_id": "2026-04-20T19:32:24+00:00_11",
        "captured_at": "2026-04-20T19:32:24+00:00",
        "world": {
            "id": "10",
            "name": "Foo",
        },
        "data": [
            {
                "creature": "Dragon",
                "last_day": {
                    "players_killed": 5,
                    "creatures_killed": 10,
                },
                "last_7_days": {
                    "players_killed": 15,
                    "creatures_killed": 20,
                },
            },
            {
                "creature": "Elf Arcanist",
                "last_day": {
                    "players_killed": 0,
                    "creatures_killed": 30,
                },
                "last_7_days": {
                    "players_killed": 35,
                    "creatures_killed": 40,
                },
            },
        ],
    }

    result = provider.normalize_raw(raw)

    # root
    assert result["snapshot_id"] == raw["snapshot_id"]
    assert result["captured_at"] == raw["captured_at"]
    assert result["world_id"] == raw["world"]["id"]
    assert result["world_name"] == raw["world"]["name"]

    # data length
    assert len(result["data"]) == 2

    # item 1
    item1 = result["data"][0]
    raw1 = raw["data"][0]

    assert item1["creature"] == raw1["creature"]
    assert item1["last_day"]["players_killed"] == raw1["last_day"]["players_killed"]
    assert item1["last_day"]["creatures_killed"] == raw1["last_day"]["creatures_killed"]
    assert (
        item1["last_7_days"]["players_killed"] == raw1["last_7_days"]["players_killed"]
    )
    assert (
        item1["last_7_days"]["creatures_killed"]
        == raw1["last_7_days"]["creatures_killed"]
    )

    # item 2
    item2 = result["data"][1]
    raw2 = raw["data"][1]

    assert item2["creature"] == raw2["creature"]
    assert item2["last_day"]["players_killed"] == raw2["last_day"]["players_killed"]
    assert item2["last_day"]["creatures_killed"] == raw2["last_day"]["creatures_killed"]
    assert (
        item2["last_7_days"]["players_killed"] == raw2["last_7_days"]["players_killed"]
    )
    assert (
        item2["last_7_days"]["creatures_killed"]
        == raw2["last_7_days"]["creatures_killed"]
    )
