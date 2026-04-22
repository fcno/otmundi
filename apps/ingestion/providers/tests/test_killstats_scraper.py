from apps.ingestion.providers.killstats_scraper import (
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
                "monster": "Dragon",
                "last_day": {
                    "players_killed": 5,
                    "monsters_killed": 10,
                },
                "last_7_days": {
                    "players_killed": 15,
                    "monsters_killed": 20,
                },
            },
            {
                "monster": "Elf Arcanist",
                "last_day": {
                    "players_killed": 0,
                    "monsters_killed": 30,
                },
                "last_7_days": {
                    "players_killed": 35,
                    "monsters_killed": 40,
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

    assert item1["monster"] == raw1["monster"]
    assert item1["last_day"]["players_killed"] == raw1["last_day"]["players_killed"]
    assert item1["last_day"]["monsters_killed"] == raw1["last_day"]["monsters_killed"]
    assert item1["last_7_days"]["players_killed"] == raw1["last_7_days"]["players_killed"]
    assert item1["last_7_days"]["monsters_killed"] == raw1["last_7_days"]["monsters_killed"]

    # item 2
    item2 = result["data"][1]
    raw2 = raw["data"][1]

    assert item2["monster"] == raw2["monster"]
    assert item2["last_day"]["players_killed"] == raw2["last_day"]["players_killed"]
    assert item2["last_day"]["monsters_killed"] == raw2["last_day"]["monsters_killed"]
    assert item2["last_7_days"]["players_killed"] == raw2["last_7_days"]["players_killed"]
    assert item2["last_7_days"]["monsters_killed"] == raw2["last_7_days"]["monsters_killed"]