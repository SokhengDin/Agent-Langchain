#!/bin/bash

create_directory() { mkdir -p "$1"; }
create_file() { touch "$1"; }

print_header() {
    echo "
╔═══════════════════════════════════════════╗
║     🚀 🌟 🔧 🐍 🚀 🌟 🔧 🐍 🚀 🌟 🔧 🐍     ║
║                                           ║
║     FastAPI Project Structure Generator   ║
║                                           ║
║     🚀 🌟 🔧 🐍 🚀 🌟 🔧 🐍 🚀 🌟 🔧 🐍     ║
╚═══════════════════════════════════════════╝"
}

get_user_input() {
    local prompt=$1
    local array_name=$2
    local items=()
    echo -e "\n$prompt (press Enter on an empty line to finish):"
    while true; do
        read -p "  > " item
        [[ -z $item ]] && break
        items+=("$item")
    done
    eval $array_name='("${items[@]}")'
}

create_project_structure() {
    local project_name=$1
    local requirements=("${!2}")
    local env_vars=("${!3}")

    echo -e "\n🏗️  Creating project structure for '$project_name'..."
    create_directory "$project_name" && cd "$project_name"

    create_file "Dockerfile"
    echo "🐳 Created Dockerfile"
    
    create_file "main.py"
    echo "🐍 Created main.py"

    if [ ${#requirements[@]} -ne 0 ]; then
        printf "%s\n" "${requirements[@]}" > requirements.txt
        echo "📋 Created requirements.txt"
    fi

    if [ ${#env_vars[@]} -ne 0 ]; then
        printf "%s\n" "${env_vars[@]}" > .env.example
        echo "🔐 Created .env.example"
    fi

    create_directory "app" && create_file "app/__init__.py"
    echo "📁 Created app directory"

    create_directory "app/api" && create_file "app/api/__init__.py"
    echo "🌐 Created API directory"

    create_directory "app/api/deps" && create_file "app/api/deps/__init__.py"
    echo "🔗 Created API deps directory"

    create_directory "app/api/v1" && create_file "app/api/v1/__init__.py"
    create_file "app/api/v1/router.py"
    echo "🚀 Created API v1 directory and router"

    create_directory "app/api/v1/handlers" && create_file "app/api/v1/handlers/__init__.py"
    echo "🎮 Created API v1 handlers directory"

    create_directory "app/core" && create_file "app/core/__init__.py"
    create_file "app/core/config.py"
    echo "🧠 Created core directory and config file"

    create_directory "app/core/enum" && create_file "app/core/enum/__init__.py"
    echo "🔢 Created core enum directory"

    create_directory "app/core/utils" && create_file "app/core/utils/__init__.py"
    echo "🛠️  Created core utils directory"

    create_directory "app/middleware" && create_file "app/middleware/__init__.py"
    echo "🔀 Created middleware directory"

    create_directory "app/models" && create_file "app/models/__init__.py"
    echo "💾 Created models directory"

    create_directory "app/schemas" && create_file "app/schemas/__init__.py"
    echo "📊 Created schemas directory"

    create_directory "app/services" && create_file "app/services/__init__.py"
    echo "🔧 Created services directory"

    create_directory "app/tests"
    echo "🧪 Created tests directory"

    echo "✨ FastAPI project structure created successfully!"
}

main() {
    print_header

    echo -e "\n📛 Enter your project name:"
    read -p "  > " project_name
    
    local requirements env_vars
    read -p $'\n📋 Include requirements.txt? (y/n): ' include_requirements
    [[ $include_requirements == "y" ]] && get_user_input "📚 Enter your required libraries" requirements

    read -p $'\n🔐 Include .env.example? (y/n): ' include_env
    [[ $include_env == "y" ]] && get_user_input "🔑 Enter your environment variables" env_vars

    create_project_structure "$project_name" requirements[@] env_vars[@]

    echo -e "\n🎉 All done! Happy coding! 🎉"
}

main
