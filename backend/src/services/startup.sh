#!/bin/bash
#japierdolepomocy

# Minecraft Server Startup Script
set -e

echo "Starting Minecraft Server"
echo "MC Version: $MC_VERSION"
echo "Loader: $LOADER"

# Handle memory settings - add M suffix if just a number (no unit)
XMX=${XMX:-512}
XMS=${XMS:-512}
# Check if value is just digits (no M, G, etc suffix)
if [[ $XMX =~ ^[0-9]+$ ]]; then
    XMX="${XMX}M"
fi
if [[ $XMS =~ ^[0-9]+$ ]]; then
    XMS="${XMS}M"
fi

EULA=${EULA:-true}
echo "JVM Memory: Xmx=${XMX} Xms=${XMS}"
echo "EULA: $EULA"

# Always create/update EULA file with the current setting
echo "eula=$EULA" > /server/eula.txt
echo "Created eula.txt with eula=$EULA"

# Set Java options with dynamic memory settings
export JAVA_OPTS="-Xmx${XMX} -Xms${XMS} -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# Handle different loaders
if [ "$LOADER" = "fabric" ]; then
    echo "Setting up Fabric loader"
    
    # Check if server is already set up
    if [ -f /server/fabric-server-launch.jar ]; then
        echo "Fabric server already installed, starting..."
    else
        # Download Fabric installer
        echo "Downloading Fabric installer from: $SERVER_JAR"
        curl -L -o /server/fabric-installer.jar "$SERVER_JAR"
        
        # Run Fabric installer
        echo "Running Fabric installer for MC $MC_VERSION"
        cd /server
        java -jar fabric-installer.jar server -dir . -mcversion "$MC_VERSION" -downloadMinecraft
    fi
    
    # Start Fabric server
    echo "Starting Fabric server with Java $JAVA_VERSION"
    cd /server
    java $JAVA_OPTS -jar fabric-server-launch.jar nogui

elif [ "$LOADER" = "forge" ]; then
    echo "Setting up Forge loader"
    
    # Find existing Forge server jar
    FORGE_JAR=$(find /server -maxdepth 1 -name "forge-*.jar" -o -name "minecraft_server.*.jar" | grep -v installer | head -1)
    
    if [ -n "$FORGE_JAR" ] && [ -f "$FORGE_JAR" ]; then
        echo "Forge server already installed: $FORGE_JAR"
    else
        # Download Forge installer
        echo "Downloading Forge installer from: $SERVER_JAR"
        curl -L -o /server/forge-installer.jar "$SERVER_JAR"
        
        # Run Forge installer in headless mode
        echo "Running Forge installer in headless mode"
        cd /server
        java -Djava.awt.headless=true -jar forge-installer.jar --installServer
        
        # Find the Forge server jar
        FORGE_JAR=$(find /server -maxdepth 1 -name "forge-*.jar" -o -name "minecraft_server.*.jar" | grep -v installer | head -1)
        if [ -z "$FORGE_JAR" ]; then
            echo "ERROR: Forge server jar not found after installation!"
            exit 1
        fi
    fi
    
    echo "Starting Forge server with: $FORGE_JAR"
    cd /server
    java $JAVA_OPTS -jar "$FORGE_JAR" nogui

elif [ "$LOADER" = "neoforge" ]; then
    echo "Setting up NeoForge loader"
    
    # Download NeoForge installer
    if [ ! -f /server/neoforge-installer.jar ]; then
        echo "Downloading NeoForge installer from: $SERVER_JAR"
        curl -L -o /server/neoforge-installer.jar "$SERVER_JAR"
    fi
    
    # Run NeoForge installer to extract server jar and generate run script
    echo "Running NeoForge installer"
    cd /server
    java -jar neoforge-installer.jar --install-server
    
    # Update JVM args in the generated run.sh file
    if [ -f /server/user_jvm_args.txt ]; then
        echo "Updating user_jvm_args.txt with JVM settings"
        # Backup original
        cp /server/user_jvm_args.txt /server/user_jvm_args.txt.bak
        # Clear and add new settings (use XMX and XMS which already have units)
        echo "-Xmx${XMX}" > /server/user_jvm_args.txt
        echo "-Xms${XMS}" >> /server/user_jvm_args.txt
        echo "-XX:+UseG1GC" >> /server/user_jvm_args.txt
        echo "-XX:MaxGCPauseMillis=200" >> /server/user_jvm_args.txt
    fi
    
    # Run the NeoForge server using its generated run script
    if [ -f /server/run.sh ]; then
        echo "Starting NeoForge server using generated run.sh"
        chmod +x /server/run.sh
        /server/run.sh nogui
    else
        echo "ERROR: NeoForge run.sh not generated!"
        exit 1
    fi

elif [ "$LOADER" = "vanilla" ]; then
    # Default behavior for vanilla - download and run server.jar
    echo "Setting up Vanilla server"
    rm -f /server/server.jar
    
    if [ ! -f /server/server.jar ]; then
        echo "Downloading server.jar from: $SERVER_JAR"
        echo $SERVER_JAR
        curl -L -o /server/server.jar "$SERVER_JAR"
        if [ ! -f /server/server.jar ]; then
            echo "ERROR: Failed to download server.jar"
            exit 1
        fi
        echo "server.jar downloaded successfully"
    fi
    
    echo "Starting Vanilla server with Java $JAVA_VERSION"
    cd /server
    java $JAVA_OPTS -jar /server/server.jar nogui
fi