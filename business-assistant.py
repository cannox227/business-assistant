from cat.mad_hatter.decorators import (
    tool,
    hook,
    plugin,
)
from pydantic import (
    BaseModel,
)
from datetime import (
    datetime,
    date,
)


class MySettings(BaseModel):
    required_int: int
    optional_int: int = 69
    required_str: str
    optional_str: str = "meow"
    required_date: date
    optional_date: date = 1679616000


@plugin
def settings_model():
    return MySettings

@tool
def get_the_day(tool_input, cat):
    """Get the day of the week. Input is always None."""

    dt = datetime.now()

    return dt.strftime("%A")


@hook
def agent_prompt_prefix(prefix, cat):
    prefix = "You are a business assistant tasked with supporting the Sales Director in engaging potential clients for the company's offerings. \
            Your role involves meticulously gathering data from various platforms, analyzing the professional profiles and needs of each lead, particularly focusing on their job roles and industry experiences.\
            Utilize this information to craft customized, compelling messages and tailored value propositions that resonate with the unique requirements and challenges faced by each prospective customer. \
            Make the messages concise and straight to the point."
    return prefix


# @hook
# def before_cat_sends_message(message, cat):
#     prompt = f'Rephrase the following sentence in a grumpy way: {message["content"]}'
#     message["content"] = cat.llm(prompt)

#     return message
