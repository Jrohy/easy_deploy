# main function bound to gosuncn command
function _auto_tab() {
	local options_array=("push" "pull" "info" "run" "-h")
	local keyword_array=("172.16.11.101" "172.16.11.77" "172.16.13.199" "172.16.16.12" "192.168.36.93")
	local cur pre

	COMPREPLY=()
	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"

	if [[ $COMP_CWORD -ge 3 ]]; then
		COMPREPLY=( $(compgen -W "${keyword_array[*]}" -- $cur) )
	fi

	case $prev in
		'gosuncn')
			COMPREPLY=( $(compgen -W "${options_array[*]}" -- $cur) ) ;;
		'push')
			compopt -o nospace
			COMPREPLY=( $(compgen -d -f ${cur}) );;
		'pull')
			compopt -o nospace
			COMPREPLY=( $(compgen -d -f ${cur}) );;
		'run')
			#命令补全后不要多加空格
			compopt -o nospace
			COMPREPLY=( $(compgen -W "\'\'" -- $cur) ) ;;
		'*')
			COMPREPLY=( $(compgen -d -f ${cur}) ) ;;
	esac


	return 0
}
complete -F _auto_tab easy_deploy