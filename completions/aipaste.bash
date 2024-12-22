_aipaste_completion() {
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # List of top-level commands:
    local commands="snap tokens completion stream"

    case "${COMP_WORDS[1]}" in
        snap)
            local snap_opts="--path --output --summary --no-summary --max-file-size --force --skip-common --skip-files --help"
            case "${prev}" in
                --path|-p)
                    COMPREPLY=( $(compgen -d -- "${cur}") )
                    return 0
                    ;;
                --output|-o)
                    COMPREPLY=( $(compgen -f -- "${cur}") )
                    return 0
                    ;;
                --skip-files)
                    COMPREPLY=( $(compgen -f -- "${cur}") )
                    return 0
                    ;;
            esac
            if [[ "${cur}" == -* ]]; then
                COMPREPLY=( $(compgen -W "${snap_opts}" -- "${cur}") )
            fi
            return 0
            ;;
        stream)
            local stream_opts="--path --max-file-size --skip-common --skip-files --help"
            case "${prev}" in
                --path|-p)
                    COMPREPLY=( $(compgen -d -- "${cur}") )
                    return 0
                    ;;
                --skip-files)
                    COMPREPLY=( $(compgen -f -- "${cur}") )
                    return 0
                    ;;
            esac
            if [[ "${cur}" == -* ]]; then
                COMPREPLY=( $(compgen -W "${stream_opts}" -- "${cur}") )
            fi
            return 0
            ;;
        tokens)
            # Optional file arg
            COMPREPLY=( $(compgen -f -- "${cur}") )
            return 0
            ;;
        completion)
            COMPREPLY=( $(compgen -W "bash zsh fish" -- "${cur}") )
            return 0
            ;;
    esac

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${commands}" -- "${cur}") )
    fi

    return 0
}

complete -F _aipaste_completion aipaste