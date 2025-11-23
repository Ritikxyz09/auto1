def auto_fix_code(code):
    fixed = code

    # -------- BASIC ERROR FIXES --------
    fixes = [
        ("print ", "print("),
        (" input ", " input("),
        ("asyncio.run(", "asyncio.run("),
    ]

    for old, new in fixes:
        fixed = fixed.replace(old, new)

    # Auto add missing closing parenthesis
    if fixed.count("(") > fixed.count(")"):
        fixed += ")"

    return fixed
