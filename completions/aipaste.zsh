#compdef aipaste

_aipaste() {
    local -a commands
    commands=(
        'snap:Create a markdown snapshot of your project'
        'tokens:Detailed token analysis for your project'
        'completion:Generate shell completion script'
    )

    case $words[1] in
        snap)
            _arguments -C \
                '(-p --path)'{-p,--path}'[Path to project directory]:directory:_files -/' \
                '(-o --output)'{-o,--output}'[Output markdown file]:file:_files' \
                '--summary[Show stats]' \
                '--no-summary[Hide stats]' \
                '--max-file-size[Max file size]:size' \
                '-f[Force overwrite]' \
                '--skip-common[Skip common files]' \
                '--skip-files[Additional skip patterns]:pattern:_files' \
                '--help[Show help]' \
                '*:: :->end'
            ;;
        tokens)
            # Single optional FILE argument
            _arguments -C '*:file:_files'
            ;;
        completion)
            _values 'shell' bash zsh fish
            ;;
        *)
            _describe -t commands 'commands' commands
            ;;
    esac
}

_aipaste "$@"

