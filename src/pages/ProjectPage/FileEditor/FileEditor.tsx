import { FunctionComponent } from "react";
import FigurlFileEditor from "./FigurlFileEditor";
import NwbFileEditor from "./NwbFileEditor";
import OtherFileEditor from "./OtherFileEditor";
import Nh5FileEditor from "./Nh5FileEditor";

type Props = {
    fileName: string
    width: number
    height: number
}

const FileEditor: FunctionComponent<Props> = ({fileName, width, height}) => {
    if (fileName.endsWith('.nwb')) {
        return (
            <NwbFileEditor
                fileName={fileName}
                width={width}
                height={height}
            />
        )
    }
    else if (fileName.endsWith('.nh5')) {
        return (
            <Nh5FileEditor
                fileName={fileName}
                width={width}
                height={height}
            />
        )
    }
    else if (fileName.endsWith('.figurl')) {
        return (
            <FigurlFileEditor
                fileName={fileName}
                width={width}
                height={height}
            />
        )
    }
    else {
        return (
            <OtherFileEditor
                fileName={fileName}
                width={width}
                height={height}
            />
        )
    }
}

export default FileEditor