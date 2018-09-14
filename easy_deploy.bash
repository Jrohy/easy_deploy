# main function bound to gosuncn command
function _auto_tab() {
	local local_file_array=($(ls))
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
		'easy_deploy')
			COMPREPLY=( $(compgen -W "${options_array[*]}" -- $cur) ) ;;
		'push')
			COMPREPLY=( $(compgen -W "${local_file_array[*]}" -- $cur) ) ;;
		'pull')
			COMPREPLY=( $(compgen -W "${local_file_array[*]}" -- $cur) ) ;;
		'run')
			#命令补全后不要多加空格
			compopt -o nospace
			COMPREPLY=( $(compgen -W "\'\'" -- $cur) ) ;;
		'*')
			COMPREPLY=( $(compgen -W "${local_file_array[*]}" -- $cur) ) ;;
	esac

	return 0
}
complete -F _auto_tab easy_deploy