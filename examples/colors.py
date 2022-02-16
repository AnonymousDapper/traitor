# The MIT License (MIT)

# Copyright (c) 2022 AnonymousDapper

# type: ignore

from traitor import impl
from traitor.traits.colored import ColoredString, Colorize

print("this is blue".blue())

print("this is red".red())

print("this is red on blue".red().on_blue())

print("this is also red on blue".on_blue().red())

print("you can use truecolor values too!".truecolor(0, 255, 136))

print("background truecolor also works :)".on_truecolor(135, 167, 78).bright_white().bold())

print("you can also make bold comments".bold())

print("{} {} {}".format("or use".cyan(), "any".italic().yellow(), "string type".cyan()))

print("or change advice. This is red".yellow().blue().red())

print("or clear things up. This is default color and style".red().bold().clear())

print("bright colors are also allowed".bright_blue().on_bright_white())

print(ColoredString("this also works!").green().bold())

print("{:50}".format("format works as expected. This will be padded".blue().on_white()))

print("{:.3}".format("and this will be green but truncated to 3 chars".green()))
