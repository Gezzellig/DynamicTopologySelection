from kubernetes_tools import extract_pods
from kubernetes_tools.add_pod import add_pod_deployment
from kubernetes_tools.delete_pod import delete_pod_deployment
from kubernetes_tools.migrate_pod import migrate_pod, PodException


class PodHasScaledWhileEnforcingException(PodException):
    pass


def state_to_generate_name_count(state):
    generate_name_count = {}
    for name, info in state.items():
        gen_name = info["pod_generate_name"]
        if gen_name in generate_name_count:
            generate_name_count[gen_name] += 1
        else:
            generate_name_count[gen_name] = 1
    return generate_name_count


def update_decrease_supposed_generate_name_count(generate_name, cur_counter):
    cur_counter[generate_name] -= 1


def update_increase_supposed_generate_name_count(generate_name, cur_counter):
    cur_counter[generate_name] += 1


def check_current_state(initial_generate_name_count):
    current_state = extract_pods.extract_all_pods()
    current_generate_name_count = state_to_generate_name_count(current_state)
    if not initial_generate_name_count == current_generate_name_count:
        raise PodHasScaledWhileEnforcingException()


def enforce_downscaling(downscalers, initial_state):
    supposed_generate_name_count = state_to_generate_name_count(initial_state)
    for downscaler in downscalers:
        pod_name = downscaler["pod_name"]
        generate_name = downscaler["pod_generate_name"]
        deployment_name = downscaler["deployment_name"]
        namespace = downscaler["namespace"]

        delete_pod_deployment(pod_name, deployment_name, namespace)
        update_decrease_supposed_generate_name_count(generate_name, supposed_generate_name_count)
        check_current_state(supposed_generate_name_count)


def enforce_migrations(migrations, initial_state):
    initial_generate_name_count = state_to_generate_name_count(initial_state)
    for migration in migrations:
        pod_name = migration["pod_name"]
        destination_node = migration["destination"]
        print("performing movement: {} to {}".format(pod_name, destination_node))
        migrate_pod(pod_name, destination_node)
        check_current_state(initial_generate_name_count)


def enforce_upscaling(upscalers, initial_state):
    supposed_generate_name_count = state_to_generate_name_count(initial_state)
    for upscaler in upscalers:
        destination_node = upscaler["destination_node"]
        generate_name = upscaler["pod_generate_name"]
        deployment_name = upscaler["deployment_name"]
        namespace = upscaler["namespace"]

        add_pod_deployment(destination_node, deployment_name, namespace)
        update_increase_supposed_generate_name_count(generate_name, supposed_generate_name_count)
        check_current_state(supposed_generate_name_count)


def enforce(downscalers, migrations, upscalers):
    cur_state = extract_pods.extract_all_pods()
    enforce_downscaling(downscalers, cur_state)
    cur_state = extract_pods.extract_all_pods()
    enforce_migrations(migrations, cur_state)
    cur_state = extract_pods.extract_all_pods()
    enforce_upscaling(upscalers, cur_state)

