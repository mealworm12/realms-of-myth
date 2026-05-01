# Realms of Myth - Start Game Function
# Teleports player to class selection altar and begins the journey

# Clear inventory
clear @s

# Give ability trigger items
give @s nether_star
give @s blaze_powder
give @s ghast_tear

# Teleport to spawn (adjust coordinates for your world)
tp @s 0 70 0

# Welcome message
tellraw @s {"rawtext":[{"text":"§6══════════════════════════════════"},{"text":"\n"},{"text":"§e§lRealms of Myth"},{"text":"\n"},{"text":"§7Find the Ancient Altar and interact with The Oracle"},{"text":"\n"},{"text":"§7to choose your race and class."},{"text":"\n"},{"text":"§6══════════════════════════════════"}]}

# Give starter kit
give @s iron_sword
give @s iron_pickaxe
give @s iron_axe
give @s bread 16
