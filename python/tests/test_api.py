import pytest


@pytest.mark.asyncio
@pytest.mark.api
async def test_api():
    # important to put the tests inside so we don't get an import error when running the non-api tests
    from protocaas.api_helpers.core.protocaas_types import ProtocaasProjectUser, ComputeResourceSpecProcessor
    from protocaas.api_helpers.clients._get_mongo_client import _set_use_mock_mongo_client
    from protocaas.api_helpers.clients.pubsub import _set_use_mock_pubsub_client
    from protocaas.api_helpers.routers.gui._authenticate_gui_request import _create_mock_github_access_token
    from protocaas.common._crypto_keys import generate_keypair, _sign_message_str
    from protocaas.api_helpers.routers.gui.project_routes import create_project, CreateProjectRequest
    from protocaas.api_helpers.routers.gui.project_routes import set_project_name, SetProjectNameRequest
    from protocaas.api_helpers.routers.gui.project_routes import set_project_description, SetProjectDescriptionRequest
    from protocaas.api_helpers.routers.gui.project_routes import set_project_tags, SetProjectTagsRequest
    from protocaas.api_helpers.routers.gui.project_routes import set_project_public, SetProjectPubliclyReadableRequest
    from protocaas.api_helpers.routers.gui.project_routes import set_project_compute_resource_id, SetProjectComputeResourceIdRequest
    from protocaas.api_helpers.routers.gui.project_routes import set_project_users, SetProjectUsersRequest
    from protocaas.api_helpers.routers.gui.project_routes import get_project
    from protocaas.api_helpers.routers.gui.project_routes import get_projects
    from protocaas.api_helpers.routers.gui.project_routes import delete_project
    from protocaas.api_helpers.routers.gui.project_routes import get_jobs
    from protocaas.api_helpers.routers.gui.create_job_route import create_job_handler, CreateJobRequest
    from protocaas.api_helpers.routers.gui.job_routes import get_job
    from protocaas.api_helpers.routers.gui.job_routes import delete_job
    from protocaas.api_helpers.routers.compute_resource.router import compute_resource_get_unfinished_jobs
    from protocaas.api_helpers.routers.processor.router import processor_update_job_status, ProcessorUpdateJobStatusRequest

    _set_use_mock_mongo_client(True)
    _set_use_mock_pubsub_client(True)
    github_access_token = _create_mock_github_access_token()

    # Generate compute resource keys
    public_key_hex, private_key_hex = generate_keypair()
    compute_resource_id = public_key_hex
    compute_resource_private_key = private_key_hex

    # gui: Create projects
    req = CreateProjectRequest(
        name='project1'
    )
    resp = await create_project(data=req, github_access_token=github_access_token)
    assert resp.success
    project1_id = resp.projectId
    req = CreateProjectRequest(
        name='project2'
    )
    resp = await create_project(data=req, github_access_token=github_access_token)
    assert resp.success
    project2_id = resp.projectId

    # gui: Set project name
    req = SetProjectNameRequest(
        name='project1_renamed'
    )
    resp = await set_project_name(project_id=project1_id, data=req, github_access_token=github_access_token)
    assert resp.success

    # gui: Set project description
    req = SetProjectDescriptionRequest(
        description='project1_description'
    )
    resp = await set_project_description(project_id=project1_id, data=req, github_access_token=github_access_token)
    assert resp.success

    # gui: Set project tags
    req = SetProjectTagsRequest(
        tags=['tag1', 'tag2']
    )
    resp = await set_project_tags(project_id=project1_id, data=req, github_access_token=github_access_token)
    assert resp.success

    # gui: Get project
    resp = await get_project(project_id=project1_id)
    project = resp.project
    assert project.projectId == project1_id
    assert project.name == 'project1_renamed'
    assert project.description == 'project1_description'
    assert project.ownerId == 'github|__mock__user'
    assert project.users == []
    assert project.publiclyReadable is True
    assert project.tags == ['tag1', 'tag2']
    assert project.timestampCreated > 0
    assert project.timestampModified > 0
    assert project.computeResourceId is None

    # gui: Set project publicly readable
    req = SetProjectPubliclyReadableRequest(
        publiclyReadable=False
    )
    resp = await set_project_public(project_id=project1_id, data=req, github_access_token=github_access_token)
    assert resp.success

    # gui: Set project compute resource id
    for project_id in [project1_id, project2_id]:
        req = SetProjectComputeResourceIdRequest(
            computeResourceId=compute_resource_id
        )
        resp = await set_project_compute_resource_id(project_id=project_id, data=req, github_access_token=github_access_token)
        assert resp.success

    # gui: Set project users
    req = SetProjectUsersRequest(
        users=[
            ProtocaasProjectUser(userId='github|user_viewer', role='viewer'),
            ProtocaasProjectUser(userId='github|user_editor', role='editor'),
            ProtocaasProjectUser(userId='github|user_admin', role='admin')
        ]
    )
    resp = await set_project_users(project_id=project1_id, data=req, github_access_token=github_access_token)
    assert resp.success

    # gui: Get project
    resp = await get_project(project_id=project1_id)
    project = resp.project
    assert project.publiclyReadable is False
    assert project.computeResourceId == compute_resource_id
    assert project.users == [
        ProtocaasProjectUser(userId='github|user_viewer', role='viewer'), # hmmm, how are these classes being compared?
        ProtocaasProjectUser(userId='github|user_editor', role='editor'),
        ProtocaasProjectUser(userId='github|user_admin', role='admin')
    ]

    # gui: Get all projects
    resp = await get_projects(github_access_token=github_access_token)
    projects = resp.projects
    assert len(projects) == 2
    assert project1_id in [p.projectId for p in projects]

    # gui: Delete project
    resp = await delete_project(project_id=project1_id, github_access_token=github_access_token)
    assert resp.success

    # gui: Get all projects
    resp = await get_projects(github_access_token=github_access_token)
    projects = resp.projects
    assert len(projects) == 1

    # gui: Set project compute resource id
    req = SetProjectComputeResourceIdRequest(
        computeResourceId=compute_resource_id
    )
    resp = await set_project_compute_resource_id(project_id=project2_id, data=req, github_access_token=github_access_token)
    assert resp.success

    # gui: Create job
    processor_name = 'test_processor'
    processor_spec = ComputeResourceSpecProcessor(
        name=processor_name,
        help='test help',
        inputs=[],
        outputs=[],
        parameters=[],
        attributes=[],
        tags=[]
    )
    req = CreateJobRequest(
        projectId=project2_id,
        processorName=processor_name,
        inputFiles=[],
        outputFiles=[],
        inputParameters=[],
        processorSpec=processor_spec,
        batchId=None,
        dandiApiKey=None,
    )
    resp = await create_job_handler(data=req, github_access_token=github_access_token)
    assert resp.success
    job_id = resp.jobId
    assert job_id

    # gui: Get job
    resp = await get_job(job_id=job_id)
    job = resp.job
    assert job.jobId == job_id
    assert job.projectId == project2_id
    assert job.processorName == processor_name
    assert job.inputFiles == []
    assert job.outputFiles == []
    assert job.inputParameters == []
    assert job.processorSpec == processor_spec
    assert job.batchId is None
    assert job.dandiApiKey is None
    assert job.status == 'pending'
    assert job.timestampCreated > 0
    assert job.timestampStarted is None
    assert job.timestampFinished is None
    assert job.timestampQueued is None
    assert job.timestampStarting is None
    assert job.computeResourceId == compute_resource_id
    assert not job.jobPrivateKey # should not be exposed to GUI

    # gui: Get jobs
    resp = await get_jobs(project_id=project2_id)
    jobs = resp.jobs
    assert len(jobs) == 1

    # compute_resource: Get unfinished jobs
    expected_payload = f'/api/compute_resource/compute_resources/{compute_resource_id}/unfinished_jobs'
    signature = _sign_message_str(expected_payload, compute_resource_id, compute_resource_private_key)
    resp = await compute_resource_get_unfinished_jobs(
        compute_resource_id=compute_resource_id,
        compute_resource_payload=expected_payload,
        compute_resource_signature=signature,
        compute_resource_node_id='mock_node_id',
        compute_resource_node_name='mock_node_name'
    )
    jobs = resp.jobs
    assert len(jobs) == 1
    job = jobs[0]
    assert job.jobId == job_id
    job_private_key = job.jobPrivateKey
    assert job_private_key

    # processor: Set job status to starting
    req = ProcessorUpdateJobStatusRequest(
        status='starting'
    )
    resp = await processor_update_job_status(job_id=job_id, data=req, job_private_key=job_private_key)
    assert resp.success

    # gui: Get job
    resp = await get_job(job_id=job_id)
    job = resp.job
    assert job.status == 'starting'

    # processor: Set job status to running
    req = ProcessorUpdateJobStatusRequest(
        status='running'
    )
    resp = await processor_update_job_status(job_id=job_id, data=req, job_private_key=job_private_key)
    assert resp.success

    # gui: Get job
    resp = await get_job(job_id=job_id)
    job = resp.job
    assert job.status == 'running'

    # processor: Set job console output
    # TODO: not implemented yet

    # processor: Set job status finished
    req = ProcessorUpdateJobStatusRequest(
        status='finished'
    )
    resp = await processor_update_job_status(job_id=job_id, data=req, job_private_key=job_private_key)
    assert resp.success

    # gui: Get job
    resp = await get_job(job_id=job_id)
    job = resp.job
    assert job.status == 'finished'

    # gui: Delete job
    resp = await delete_job(job_id=job_id, github_access_token=github_access_token)
    assert resp.success

    # gui: Get jobs
    resp = await get_jobs(project_id=project2_id)
    jobs = resp.jobs
    assert len(jobs) == 0