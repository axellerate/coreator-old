var SideMenu = React.createClass({
	render: function(){
		return(
			<div>
				<SideMenuHeader />
				<SideMenuButtons />
			</div>
		);
	}
});

React.render(
  <SideMenu />,
  document.getElementById("side-menu")
);