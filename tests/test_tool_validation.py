

# ------------------------------------------- the orientation a non-Claude-Code client receives

def test_the_server_sends_instructions_to_a_bare_client():
    """A Claude Desktop or phone client gets no CLAUDE.md and no .claude/skills/.

    In this repo a Claude Code session is handed the protocol notes and three patch skills
    automatically. Every other MCP client - Desktop, a phone, anything - is handed nothing, and
    would have to guess how to drive a Haken module. The server's `instructions` are that
    client's entire orientation, so they must survive refactoring.
    """
    from eagan_mcp import server

    text = server.mcp.instructions or ""
    assert len(text) > 500, (
        "the server sends no instructions, so a client without CLAUDE.md and the skills has no "
        "orientation at all")

    # the workflow: consult the shipped knowledge before writing MIDI
    for pointer in ("get_knowledge", "get_recipes", "search_factory_presets", "connect"):
        assert pointer in text, f"instructions never mention {pointer}"

    # the safety contract, which is the part with consequences
    assert "EDIT SLOT" in text, "instructions do not state that writes go to the edit slot"
    assert "NEVER store to a user slot" in text, (
        "instructions do not forbid an unconfirmed store; a store has no undo and can destroy "
        "a preset the user built by hand")
    assert "SEPARATE read" in text, (
        "instructions do not say to verify with a separate read rather than the write's echo")
