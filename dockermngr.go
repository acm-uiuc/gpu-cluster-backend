package dockermngr 

import (
	"io"
	"os"

	"github.com/moby/moby/api/types"
	"github.com/moby/moby/api/types/container"
	"github.com/moby/moby/client"
	"golang.org/x/net/context"
)

type DockerCtrl struct {
	cli 
	ctx 
}

func (dockerctrl* d) UpdateBox(name string) {
	return d.cli.ImagePull(d.ctx, name, types.ImagePullOptions{})
} 

func (dockerctrl* d) CreateComtainer(config container.Config) (resp, error) {
	return d.cli.ContainerCreate(d.ctx, config, nil, nil, "")
}

func (dockerctrl* d) StartComtainer(options types.ContainerStartOptions, resp) (resp, error) {
	return d.cli.ContainerStart(d.ctx, resp.ID, options)
}

func (dockerctrl* d) GetContainerLogs(options types.ContainerLogsOptions) (resp, error) {
	return d.cli.ContainerLogs(ctx, resp.ID, options)
}