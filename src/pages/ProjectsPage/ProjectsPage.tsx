import { FunctionComponent } from "react";
import ProjectsTable from "./ProjectsTable";
import useRoute from "../../useRoute";
import Hyperlink from "../../components/Hyperlink";
import './ProjectsPage.css'

type Props = {

}

const ProjectsPage: FunctionComponent<Props> = ({ }) => {
    const {setRoute} = useRoute()
    return (
        <div className="projects-page main">
            <h3>Your projects</h3>
            <ProjectsTable />
            <hr />
            <p>
                To add a project, <Hyperlink onClick={() => setRoute({page: 'dandisets'})}>navigate to a dandiset</Hyperlink> and click the button to add a project associated with that dandiset.
            </p>
        </div>
    )
}

export default ProjectsPage