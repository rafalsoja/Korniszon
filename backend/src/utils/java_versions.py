# Mapping of Minecraft versions to required Java versions
MC_TO_JAVA = {
    # Format: (major, minor) → java_version
    (1, 20): 21,  # 1.20+
    (1, 19): 17,  # 1.19
    (1, 18): 17,  # 1.18
    (1, 17): 16,  # 1.17
    (1, 16): 11,  # 1.16
    (1, 15): 11,  # 1.15
    (1, 12): 8,  # 1.12-1.15
}


def get_java_version(mc_version: str) -> int:
    parts = mc_version.split(".")
    if len(parts) < 2 or parts[0] != "1":
        raise ValueError(f"Invalid Minecraft version format: {mc_version}")

    major, minor = int(parts[0]), int(parts[1])

    # Find matching version (check from newest to oldest)
    for (req_major, req_minor), java_ver in sorted(MC_TO_JAVA.items(), reverse=True):
        if major == req_major and minor >= req_minor:
            return java_ver

    # Default to Java 21 for unknown versions
    return 21
