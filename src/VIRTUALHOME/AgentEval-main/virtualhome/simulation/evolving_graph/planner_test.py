import pddlgym_planners.pddl_planner
from pddlgym_planners.fd import FD


if __name__ == "__main__":
    # domain_file_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/pddl_files/hiking.pddl"
    domain_file_path = '/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/pddl_files/virtualhome.pddl'
    # problem_file_path = "/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/pddl_files/hiking/promblem0.pddl"
    problem_file_path = '/viscam/u/shiyuz/svl_project/AgentEval/virtualhome/resources/pddl_files/virtualhome/Wash_clothes/27_2.pddl'
    planner = FD()
    cmd_str = planner._get_cmd_str(domain_file_path, problem_file_path, 10)
    print(f'{cmd_str=}')
    pddl_plan = planner.plan_from_pddl(domain_file_path, problem_file_path)
    print(f'{pddl_plan=}')
    print("Test passed")