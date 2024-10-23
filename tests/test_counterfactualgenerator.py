import pytest
from langchain_openai import AzureChatOpenAI

from langfair.generator import CounterfactualGenerator


@pytest.mark.asyncio
async def test_counterfactual(monkeypatch):
    # TODO: Tests to check if `parse_texts` method works for all words in gender/race word list.
    # TODO: Add tests for `estimate_token_cost` method (first need to fix the bug)
    MOCKED_PROMPTS = [
        "Prompt 1: male person",
        "Prompt 2: female person",
        "Prompt 3: white person",
        "Prompt 4: black person",
    ]
    MOCKED_RACE_PROMPTS = {
        "white_prompt": ["prompt 3: white person", "prompt 4: white person"],
        "black_prompt": ["prompt 3: black person", "prompt 4: black person"],
        "hispanic_prompt": ["prompt 3: hispanic person", "prompt 4: hispanic person"],
        "asian_prompt": ["prompt 3: asian person", "prompt 4: asian person"],
        "attribute_words": [["white person"], ["black person"]],
        "original_prompt": ["Prompt 3: white person", "Prompt 4: black person"],
    }
    MOCKED_GENDER_PROMPTS = {
        "male_prompt": ["Prompt 1: male person", "Prompt 2: male person"],
        "female_prompt": ["Prompt 1: female person", "Prompt 2: female person"],
        "attribute_words": [["male"], ["female"]],
        "original_prompt": ["Prompt 1: male person", "Prompt 2: female person"],
    }
    MOCKED_CF_PROMPTS = list(MOCKED_RACE_PROMPTS.values()) + list(
        MOCKED_GENDER_PROMPTS.values()
    )
    MOCKED_RESPONSES = [
        [
            "Mocked response 1",
            "Mocked response 2",
            "Unable to get response",
            "Mocked response 4",
        ]
    ]

    async def mock_generate_in_batches(*args, **kwargs):
        return MOCKED_RESPONSES, MOCKED_CF_PROMPTS.pop(0)

    mock_object = AzureChatOpenAI(
        deployment_name="YOUR-DEPLOYMENT",
        temperature=0,
        api_key="SECRET_API_KEY",
        api_version="2024-05-01-preview",
        azure_endpoint="https://mocked.endpoint.com",
    )

    counterfactual_object = CounterfactualGenerator(langchain_llm=mock_object)

    monkeypatch.setattr(
        counterfactual_object, "_generate_in_batches", mock_generate_in_batches
    )

    race_prompts = counterfactual_object.parse_texts(
        texts=MOCKED_PROMPTS, attribute="race"
    )
    assert race_prompts == [[], [], ["white person"], ["black person"]]

    gender_prompts = counterfactual_object.parse_texts(
        texts=MOCKED_PROMPTS, attribute="gender"
    )
    assert gender_prompts == [["male"], ["female"], [], []]

    race_prompts = counterfactual_object.create_prompts(
        prompts=MOCKED_PROMPTS, attribute="race"
    )
    assert race_prompts == MOCKED_RACE_PROMPTS

    gender_prompts = counterfactual_object.create_prompts(
        prompts=MOCKED_PROMPTS, attribute="gender"
    )
    assert gender_prompts == MOCKED_GENDER_PROMPTS

    cf_data = await counterfactual_object.generate_responses(
        prompts=MOCKED_PROMPTS, attribute="race", count=1
    )
    assert all(
        [
            cf_data["data"][key] == MOCKED_RESPONSES[0]
            for key in cf_data["data"]
            if "response" in key
        ]
    )

    cf_data = await counterfactual_object.generate_responses(
        prompts=MOCKED_PROMPTS, attribute="gender", count=1
    )
    assert all(
        [
            cf_data["data"][key] == MOCKED_RESPONSES[0]
            for key in cf_data["data"]
            if "response" in key
        ]
    )
