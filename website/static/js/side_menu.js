

var SideMenuButtons = React.createClass({
	render: function(){
		return(
			<ul className="nav nav-pills nav-stacked">
			  <li><a href="#"><i className="fa fa-th"></i> Projects</a></li>
			  <li><a href="#"><i className="fa fa-users"></i> People</a></li>
			</ul>
		);
	}
});


var SideMenuProfileImage = React.createClass({
	render: function(){
	    return (
	        <div id="side_menu_profile_image"></div>
	    );
	}
});


var SideMenuUserInfo = React.createClass({
	render: function(){
	    return (
	        <div id="side_menu_user_info">
	        	Kris Vukasinovic
	        </div>
	    );
	}
});



var SideMenuHeader = React.createClass({
	render: function(){
	    return (
	        <div id="side_menu_header">
	        <SideMenuProfileImage />
	        <SideMenuUserInfo />
	        </div>
	    );
	}
});


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