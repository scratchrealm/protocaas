import { FunctionComponent, useState } from "react"
import Hyperlink from "../../components/Hyperlink"
import { useProject } from "./ProjectPageContext"
import ComputeResourceNameDisplay from "../../ComputeResourceNameDisplay"
import { useComputeResources } from "../ComputeResourcesPage/ComputeResourcesContext"
import ComputeResourceAppsTable2 from "./ComputeResourceAppsTable2/ComputeResourceAppsTable2"

type Props = {
    //
}

const ComputeResourceSection: FunctionComponent<Props> = () => {
    const {project} = useProject()
    const [expanded, setExpanded] = useState(false)

    const computeResourceId = project?.computeResourceId

    if (!project) {
        return <div>Loading project...</div>
    }

    const topPart = (
        <>
            <div>&nbsp;</div>
            <div>Using compute resource: <ComputeResourceNameDisplay computeResourceId={computeResourceId || undefined} /></div>
            <div>&nbsp;</div>
        </>
    )

    if (!expanded) {
        return (
            <div>
                {topPart}
                <Hyperlink onClick={() => { setExpanded(!expanded) }}>Show more...</Hyperlink>
            </div>
        )
    }
    else {
        return (
            <div>
                {topPart}

                <SelectComputeResourceSubsection />

                <div>&nbsp;</div>
                <Hyperlink onClick={() => { setExpanded(!expanded) }}>Show less...</Hyperlink>
            </div>
        )
    }
}

const SelectComputeResourceSubsection: FunctionComponent = () => {
    const {project, projectRole, setProjectComputeResourceId} = useProject()
    const [editing, setEditing] = useState(false)

    const computeResourceId: string | undefined = project ? (project.computeResourceId || import.meta.env.VITE_DEFAULT_COMPUTE_RESOURCE_ID) : undefined

    return (
        <div>
            {
                project && !editing && projectRole === 'admin' && (
                    <Hyperlink onClick={() => setEditing(true)}>Select a different compute resource for this project</Hyperlink>
                )
            }
            {
                project && editing && projectRole === 'admin' && (
                    <SelectComputeResourceComponent
                        selectedComputeResourceId={project.computeResourceId || undefined}
                        onSelected={(computeResourceId) => {
                            setProjectComputeResourceId(computeResourceId || '')
                            setEditing(false)
                        }}
                        onCancel={() => setEditing(false)}
                    />
                )
            }
            <div>&nbsp;</div>
            {project && computeResourceId && <ComputeResourceAppsTable2
                computeResourceId={computeResourceId}
            />}
        </div>
    )
}

type SelectComputeResourceComponentProps = {
    selectedComputeResourceId?: string
    onSelected: (computeResourceId: string) => void
    onCancel: () => void
}

const SelectComputeResourceComponent: FunctionComponent<SelectComputeResourceComponentProps> = ({onSelected, selectedComputeResourceId, onCancel}) => {
    const {computeResources} = useComputeResources()
    return (
        <div>
            New compute resource:&nbsp;
            <select onChange={
                e => {
                    const crId = e.target.value
                    if (crId === '<none>') return
                    onSelected(crId)
                }}
                value={selectedComputeResourceId || ''}>
                <option value="<none>">Select a compute resource</option>
                <option value="">DEFAULT</option>
                {
                    computeResources.map(cr => (
                        <option key={cr.computeResourceId} value={cr.computeResourceId}>{cr.name} ({abbreviate(cr.computeResourceId, 10)})</option>
                    ))
                }
            </select>
            &nbsp;
            <Hyperlink onClick={onCancel}>Cancel</Hyperlink>
        </div>
    )
}

function abbreviate(s: string, maxLength: number) {
    if (s.length <= maxLength) return s
    return s.slice(0, maxLength - 3) + '...'
}

export default ComputeResourceSection